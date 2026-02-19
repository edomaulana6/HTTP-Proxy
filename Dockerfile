# 1. Gunakan Python versi Slim agar ukuran image kecil dan hemat RAM
FROM python:3.10-slim

# 2. Instal FFMPEG (Wajib untuk menjahit audio & video agar tidak bisu)
# Serta membersihkan cache apt agar storage tetap lega
RUN apt-get update && \
    apt-get install -y ffmpeg && \
    rm -rf /var/lib/apt/lists/*

# 3. Set direktori kerja di dalam server
WORKDIR /app

# 4. Copy file requirements terlebih dahulu untuk mempercepat build
COPY requirements.txt .

# 5. Instal library Python (pyTelegramBotAPI dan yt-dlp)
RUN pip install --no-cache-dir -r requirements.txt

# 6. Copy seluruh kode bot (main.py) ke dalam server
COPY . .

# 7. Ekspos port 8000 untuk Health Check Koyeb
EXPOSE 8000

# 8. Jalankan bot
CMD ["python", "main.py"]
