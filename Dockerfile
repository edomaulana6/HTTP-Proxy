FROM python:3.10-slim

# Install ffmpeg dan pembersih cache
RUN apt-get update && apt-get install -y ffmpeg && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY . .

# Install library Python
RUN pip install --no-cache-dir pyTelegramBotAPI yt-dlp

CMD ["python", "main.py"]
