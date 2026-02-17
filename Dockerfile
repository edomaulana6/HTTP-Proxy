FROM alpine:latest

# Instalasi tools yang dibutuhkan
RUN apk add --no-cache curl unzip

# Set working directory
WORKDIR /app

# Copy konfigurasi (Pastikan Anda sudah buat file config.json di Github)
COPY config.json /app/config.json

# Download dan setup V2Ray Portable
RUN curl -L -o v2ray.zip https://github.com/v2fly/v2ray-core/releases/latest/download/v2ray-linux-64.zip \
    && unzip v2ray.zip \
    && chmod +x v2ray

# Port yang digunakan Koyeb
EXPOSE 8080

# Jalankan V2Ray
CMD ["./v2ray", "run", "-c", "config.json"]
