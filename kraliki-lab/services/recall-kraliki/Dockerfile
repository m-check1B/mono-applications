FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY backend/app ./app
COPY backend/memory ./memory

# Environment
ENV API_HOST=0.0.0.0
ENV API_PORT=3020

EXPOSE 3020

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "3020"]
