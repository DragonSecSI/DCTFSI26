# Use the official Python runtime image
FROM python:3.13  
 
RUN mkdir /app
WORKDIR /app

# Install MySQL client dependencies
RUN apt-get update && apt-get install -y \
    default-libmysqlclient-dev \
    build-essential \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Set environment variables 
# Prevents Python from writing pyc files to disk
ENV PYTHONDONTWRITEBYTECODE=1
#Prevents Python from buffering stdout and stderr
ENV PYTHONUNBUFFERED=1

# CTF Flag - change this before deploying
ENV FLAG=dctf{fake_flag}
  
COPY requirements.txt  /app/
 
RUN pip install --no-cache-dir -r requirements.txt
 
COPY . /app/
 
EXPOSE 8000

CMD ["sh","-c", "python manage.py migrate && python manage.py runserver 0.0.0.0:8000"]