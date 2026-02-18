FROM python:3.10-slim
RUN apt-get update && apt-get install -y ffmpeg && pip install pyTelegramBotAPI yt-dlp
WORKDIR /app
COPY . .
CMD ["python", "main.py"]
