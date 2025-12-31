FROM python:3.13-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY schema.sql usage_tracker.py api.py dashboard.html ./

# Create data directory
RUN mkdir -p /data

EXPOSE 8585

CMD ["python", "api.py", "--port", "8585", "--db", "/data/usage.db"]
