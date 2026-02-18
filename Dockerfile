FROM python:3.10-slim

# Install tools yang dibutuhkan
RUN apt-get update && apt-get install -y ffmpeg && \
    pip install --no-cache-dir yt-dlp pyTelegramBotAPI

WORKDIR /app

# Salin semua file dari GitHub ke dalam container
COPY . .

# Jalankan python secara langsung ke file main.py
CMD ["python", "main.py"]
