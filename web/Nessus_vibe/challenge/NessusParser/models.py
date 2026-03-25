from django.db import models

# Create your models here.

class Project(models.Model):
    """Model to store project information for grouping scans"""
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['name']


class NessusScan(models.Model):
    """Model to store Nessus scan information"""
    uploaded_at = models.DateTimeField(auto_now_add=True)
    filename = models.CharField(max_length=255)
    scan_name = models.CharField(max_length=255, blank=True)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='scans', null=True, blank=True)
    
    def __str__(self):
        return f"{self.filename} - {self.uploaded_at}"
    
    class Meta:
        ordering = ['-uploaded_at']


class NessusVulnerability(models.Model):
    """Model to store individual vulnerabilities from Nessus scan"""
    
    SEVERITY_CHOICES = [
        (0, 'Info'),
        (1, 'Low'),
        (2, 'Medium'),
        (3, 'High'),
        (4, 'Critical'),
    ]
    
    scan = models.ForeignKey(NessusScan, on_delete=models.CASCADE, related_name='vulnerabilities')
    plugin_id = models.CharField(max_length=50)
    plugin_name = models.CharField(max_length=500)
    severity = models.IntegerField(choices=SEVERITY_CHOICES, default=0)
    host = models.CharField(max_length=255)
    port = models.CharField(max_length=50, blank=True)
    protocol = models.CharField(max_length=50, blank=True)
    description = models.TextField(blank=True)
    solution = models.TextField(blank=True)
    risk_factor = models.CharField(max_length=50, blank=True)
    plugin_output = models.TextField(blank=True)
    cvss_score = models.CharField(max_length=10, blank=True)
    
    def __str__(self):
        return f"{self.host} - {self.plugin_name}"
    
    def get_severity_color(self):
        """Return color code based on severity"""
        colors = {
            0: '#0288D1',  # Info - Blue
            1: '#FFB300',  # Low - Yellow
            2: '#FB8C00',  # Medium - Orange
            3: '#E53935',  # High - Red
            4: '#6A1B9A',  # Critical - Purple
        }
        return colors.get(self.severity, '#757575')
    
    def get_severity_display_text(self):
        """Return severity text"""
        return dict(self.SEVERITY_CHOICES).get(self.severity, 'Unknown')
    
    class Meta:
        ordering = ['-severity', 'host', 'plugin_name']
