FROM python:3.9
WORKDIR /app
COPY main.py .
RUN pip install fastapi uvicorn pika pydantic
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001"]