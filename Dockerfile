FROM alpine:latest
RUN apk add --no-cache wget gunzip
RUN wget https://github.com/ginuerzh/gost/releases/download/v2.11.5/gost-linux-amd64.gz
RUN gunzip gost-linux-amd64.gz
RUN chmod +x gost-linux-amd64
RUN mv gost-linux-amd64 /usr/bin/gost
EXPOSE 8080
CMD ["gost", "-L", "admin:rahasia123@:8080"]
