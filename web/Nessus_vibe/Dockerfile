FROM python:3.14-alpine
WORKDIR /app

RUN pip install --no-cache-dir flask
COPY server.py /app
COPY flag.txt /flag.txt
CMD ["python", "server.py"]
