FROM python:3.12-alpine

WORKDIR /app

RUN pip install --no-cache-dir flask mysql-connector-python

RUN mkdir db
COPY main.py .

EXPOSE 8000

CMD ["python", "main.py"]
