FROM python:3.10-slim

# Install ffmpeg agar video dan audio bisa digabung
RUN apt-get update && apt-get install -y ffmpeg && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Ambil file dari GitHub ke dalam server Koyeb
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY main.py .

# Pastikan eksekusi langsung lewat python
CMD ["python", "main.py"]
