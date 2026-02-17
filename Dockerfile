FROM ubuntu:latest

# 1. Install dependencies
RUN apt-get update && apt-get install -y curl unzip && rm -rf /var/lib/apt/lists/* [cite: 2025-12-27]

# 2. Setup environment
WORKDIR /app [cite: 2025-12-27]

# 3. Download & Install V2Ray
RUN curl -L -o v2ray.zip https://github.com/v2fly/v2ray-core/releases/latest/download/v2ray-linux-64.zip \
    && unzip v2ray.zip \
    && chmod +x v2ray \
    && rm v2ray.zip [cite: 2025-12-27]

# 4. Generate Config Otomatis
RUN echo '{"inbounds":[{"port":8080,"protocol":"vmess","settings":{"clients":[{"id":"b8313620-1511-4471-a244-6a83669680df"}]},"streamSettings":{"network":"ws","wsSettings":{"path":"/nganjuk-speed"}}}],"outbounds":[{"protocol":"freedom"}]}' > /app/config.json [cite: 2025-12-27]

# 5. Execution
EXPOSE 8080 [cite: 2025-12-27]
CMD ["/app/v2ray", "run", "-c", "/app/config.json"] [cite: 2025-12-27]
