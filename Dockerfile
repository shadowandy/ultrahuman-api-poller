FROM python:3.9-slim

WORKDIR /app

# Install required packages
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the script
COPY ultrahuman-api-poller.py .

# Run the script
CMD ["python", "ultrahuman-api-poller.py"]