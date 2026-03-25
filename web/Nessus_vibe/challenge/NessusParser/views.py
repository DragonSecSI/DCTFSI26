from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from .models import NessusScan, NessusVulnerability, Project
import xml.etree.ElementTree as ET
import json

def root(request):
    """Main view to display vulnerabilities and handle file upload"""
    if request.method == 'POST' and request.FILES.get('nessus_file'):
        nessus_file = request.FILES['nessus_file']
        
        try:
            # Parse the XML file
            parse_nessus_xml(nessus_file)
            messages.success(request, f'Successfully parsed {nessus_file.name}')
            return redirect('root')
        except Exception as e:
            messages.error(request, f'Error parsing file: {str(e)}')
    
    # Get all vulnerabilities from database
    vulnerabilities = NessusVulnerability.objects.select_related('scan', 'scan__project').all()
    projects = Project.objects.all().order_by('name')
    
    context = {
        'vulnerabilities': vulnerabilities,
        'projects': projects,
    }
    return render(request, 'NessusParser/index.html', context)


def parse_nessus_xml(file):
    """Parse Nessus XML file and save to database"""
    # Read and parse XML
    content = file.read()
    root = ET.fromstring(content)
    
    # Create scan record
    scan = NessusScan.objects.create(
        filename=file.name,
        scan_name=root.find('.//Report').get('name', '') if root.find('.//Report') is not None else ''
    )
    
    # Parse each ReportHost
    for report_host in root.findall('.//ReportHost'):
        host_name = report_host.get('name', '')
        
        # Parse each ReportItem (vulnerability)
        for item in report_host.findall('.//ReportItem'):
            plugin_id = item.get('pluginID', '')
            plugin_name = item.get('pluginName', '')
            port = item.get('port', '')
            protocol = item.get('protocol', '')
            severity = int(item.get('severity', '0'))
            
            # Extract additional fields
            description = ''
            solution = ''
            risk_factor = ''
            plugin_output = ''
            cvss_score = ''
            
            desc_elem = item.find('description')
            if desc_elem is not None and desc_elem.text:
                description = desc_elem.text
            
            solution_elem = item.find('solution')
            if solution_elem is not None and solution_elem.text:
                solution = solution_elem.text
            
            risk_elem = item.find('risk_factor')
            if risk_elem is not None and risk_elem.text:
                risk_factor = risk_elem.text
            
            output_elem = item.find('plugin_output')
            if output_elem is not None and output_elem.text:
                plugin_output = output_elem.text
            
            cvss_elem = item.find('cvss_base_score')
            if cvss_elem is not None and cvss_elem.text:
                cvss_score = cvss_elem.text
            
            # Create vulnerability record
            NessusVulnerability.objects.create(
                scan=scan,
                plugin_id=plugin_id,
                plugin_name=plugin_name,
                severity=severity,
                host=host_name,
                port=port,
                protocol=protocol,
                description=description,
                solution=solution,
                risk_factor=risk_factor,
                plugin_output=plugin_output,
                cvss_score=cvss_score
            )


def list_scans(request):
    """API endpoint to list all scans"""
    scans = NessusScan.objects.all().order_by('-uploaded_at')
    
    scan_data = []
    for scan in scans:
        vuln_count = NessusVulnerability.objects.filter(scan=scan).count()
        scan_data.append({
            'id': scan.id,
            'scan_name': scan.scan_name,
            'filename': scan.filename,
            'upload_date': scan.uploaded_at.isoformat(),
            'vulnerability_count': vuln_count
        })
    
    return JsonResponse({'scans': scan_data})


@require_http_methods(["POST"])
def delete_scan(request, scan_id):
    """API endpoint to delete a scan and its vulnerabilities"""
    try:
        scan = NessusScan.objects.get(id=scan_id)
        scan.delete()  # This will cascade delete all related vulnerabilities
        return JsonResponse({'success': True})
    except NessusScan.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Scan not found'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


def list_projects(request):
    """API endpoint to list all projects"""
    projects = Project.objects.all().order_by('name')
    
    project_data = []
    for project in projects:
        scan_count = NessusScan.objects.filter(project=project).count()
        project_data.append({
            'id': project.id,
            'name': project.name,
            'description': project.description,
            'scan_count': scan_count
        })
    
    return JsonResponse({'projects': project_data})


@require_http_methods(["POST"])
def create_project(request):
    """API endpoint to create a new project"""
    try:
        data = json.loads(request.body)
        name = data.get('name', '').strip()
        description = data.get('description', '').strip()
        
        if not name:
            return JsonResponse({'success': False, 'error': 'Project name is required'}, status=400)
        
        project = Project.objects.create(name=name, description=description)
        return JsonResponse({
            'success': True,
            'project': {
                'id': project.id,
                'name': project.name,
                'description': project.description,
                'scan_count': 0
            }
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@require_http_methods(["POST"])
def delete_project(request, project_id):
    """API endpoint to delete a project and all its scans"""
    try:
        project = Project.objects.get(id=project_id)
        project.delete()  # This will cascade delete all related scans and vulnerabilities
        return JsonResponse({'success': True})
    except Project.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Project not found'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


def get_project_scans(request, project_id):
    """API endpoint to get scans for a specific project"""
    try:
        project = Project.objects.get(id=project_id)
        scans = NessusScan.objects.filter(project=project).order_by('-uploaded_at')
        
        scan_data = []
        for scan in scans:
            vuln_count = NessusVulnerability.objects.filter(scan=scan).count()
            scan_data.append({
                'id': scan.id,
                'scan_name': scan.scan_name,
                'filename': scan.filename,
                'upload_date': scan.uploaded_at.isoformat(),
                'vulnerability_count': vuln_count
            })
        
        return JsonResponse({'scans': scan_data})
    except Project.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Project not found'}, status=404)


@require_http_methods(["POST"])
def assign_scan_to_project(request):
    """API endpoint to assign a scan to a project"""
    try:
        data = json.loads(request.body)
        scan_id = data.get('scan_id')
        project_id = data.get('project_id')
        
        scan = NessusScan.objects.get(id=scan_id)
        
        if project_id:
            project = Project.objects.get(id=project_id)
            scan.project = project
        else:
            scan.project = None
        
        scan.save()
        return JsonResponse({'success': True})
    except (NessusScan.DoesNotExist, Project.DoesNotExist) as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


def get_unassigned_scans(request):
    """API endpoint to get scans not assigned to any project"""
    scans = NessusScan.objects.filter(project__isnull=True).order_by('-uploaded_at')
    
    scan_data = []
    for scan in scans:
        vuln_count = NessusVulnerability.objects.filter(scan=scan).count()
        scan_data.append({
            'id': scan.id,
            'scan_name': scan.scan_name,
            'filename': scan.filename,
            'upload_date': scan.uploaded_at.isoformat(),
            'vulnerability_count': vuln_count
        })
    
    return JsonResponse({'scans': scan_data})
