FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY provisionar.py .
CMD ["python", "-u", "provisionar.py"]
