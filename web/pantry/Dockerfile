FROM python:3.13-alpine

WORKDIR /app

# Install dependencies
RUN pip install Flask

# Copy application source
COPY chall/ /app/
COPY flag.txt /flag.txt

CMD ["python3", "app.py"]
