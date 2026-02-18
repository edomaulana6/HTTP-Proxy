FROM python:3.10-slim

# Install ffmpeg dan library yang dibutuhkan
RUN apt-get update && apt-get install -y ffmpeg && \
    pip install --no-cache-dir yt-dlp pyTelegramBotAPI

WORKDIR /app

# Salin semua file dari github ke dalam folder /app
COPY . .

# Jalankan bot
CMD ["python", "main.py"]
