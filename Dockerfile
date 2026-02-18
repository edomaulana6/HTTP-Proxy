FROM python:3.10-slim

# Install FFMPEG dan utilitas sistem
RUN apt-get update && apt-get install -y ffmpeg && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY . .

# Install library python
RUN pip install --no-cache-dir -r requirements.txt

# Koyeb butuh port ini terbuka
EXPOSE 8000

CMD ["python", "main.py"]
