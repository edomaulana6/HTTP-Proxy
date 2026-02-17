FROM alpine:latest

# 1. Instalasi tools dan set folder kerja
RUN apk add --no-cache curl unzip
WORKDIR /app

# 2. Download dan Ekstrak V2Ray ke folder saat ini (.)
RUN curl -L -o v2ray.zip https://github.com/v2fly/v2ray-core/releases/latest/download/v2ray-linux-64.zip \
    && unzip v2ray.zip \
    && chmod +x v2ray \
    && rm v2ray.zip

# 3. Buat file config.json secara otomatis di dalam Docker agar tidak perlu COPY lagi
RUN echo '{\
  "inbounds": [{\
    "port": 8080,\
    "protocol": "vmess",\
    "settings": { "clients": [{ "id": "b8313620-1511-4471-a244-6a83669680df" }] },\
    "streamSettings": { "network": "ws", "wsSettings": { "path": "/nganjuk-speed" } }\
  }],\
  "outbounds": [{ "protocol": "freedom" }]\
}' > /app/config.json

# 4. Jalankan aplikasi menggunakan port 8080
EXPOSE 8080
CMD ["/app/v2ray", "run", "-c", "/app/config.json"]
