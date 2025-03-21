FROM python:3.9
WORKDIR /app
COPY main.py .
RUN pip install pika psycopg2 aio-pika asyncpg
CMD ["python", "-u", "main.py"]