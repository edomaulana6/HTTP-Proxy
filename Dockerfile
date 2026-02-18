FROM python:3.10-slim

# 1. Install FFMPEG (Hanya sekali, sangat berat jadi ditaruh di atas)
RUN apt-get update && apt-get install -y ffmpeg && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# 2. Copy requirements dulu agar caching pip bekerja (Lebih Cepat!)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 3. Baru copy sisa kode (main.py, dll)
COPY . .

# 4. Expose port 8000 (Sesuai setting Health Check Koyeb)
EXPOSE 8000

# 5. Jalankan bot
CMD ["python", "main.py"]
