FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ ./app/

# Port for FastAPI
EXPOSE 8000

ENV JWT_SECRET="super-secret-key"

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
