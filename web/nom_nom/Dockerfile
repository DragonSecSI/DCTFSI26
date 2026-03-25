FROM python:3.13-alpine

WORKDIR /app
COPY chall/ /app/
RUN pip install Flask python-dotenv && mkdir db

CMD ["sh", "-c", "python3 setup.py && python3 app.py"]
