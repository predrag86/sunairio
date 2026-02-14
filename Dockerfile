FROM python:3.12-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy app code
COPY app.py .
COPY test_app.py .

EXPOSE 8080

# Production server
CMD ["gunicorn", "-b", "0.0.0.0:8080", "app:app"]
