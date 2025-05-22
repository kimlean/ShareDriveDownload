# Dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY . .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

RUN mkdir -p /app/file

EXPOSE 3300

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "3300"]
