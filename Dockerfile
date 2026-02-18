FROM python:3.10-slim

# Install ffmpeg dan library yang dibutuhkan
RUN apt-get update && apt-get install -y ffmpeg && \
    pip install --no-cache-dir yt-dlp pyTelegramBotAPI

WORKDIR /app

# Ambil file main.py dari GitHub ke dalam server
COPY main.py .

# Jalankan perintah langsung ke file main.py (ANTI ERROR NOT FOUND)
CMD ["python", "main.py"]
