FROM python:3.10-slim

# Install ffmpeg untuk penggabungan video & audio
RUN apt-get update && apt-get install -y ffmpeg && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements dan install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy sisa file (main.py)
COPY . .

# Jalankan perintah langsung ke python
CMD ["python", "main.py"]
