FROM alpine:latest

# Instalasi tools yang dibutuhkan
RUN apk add --no-cache curl unzip

# Set working directory
WORKDIR /app

# Download V2Ray duluan agar tidak menindih config buatan kita
RUN curl -L -o v2ray.zip https://github.com/v2fly/v2ray-core/releases/latest/download/v2ray-linux-64.zip \
    && unzip v2ray.zip \
    && chmod +x v2ray \
    && rm v2ray.zip

# Baru kemudian masukkan config.json buatan kita sendiri
COPY config.json /app/config.json

# Port yang digunakan Koyeb
EXPOSE 8080

# Jalankan V2Ray
CMD ["./v2ray", "run", "-c", "config.json"]
