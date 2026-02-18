FROM python:3.10-slim

# 1. Install dependencies sistem (ffmpeg wajib untuk gabung audio+video)
RUN apt-get update && apt-get install -y ffmpeg && \
    pip install --no-cache-dir yt-dlp pyTelegramBotAPI [cite: 2025-12-27]

WORKDIR /app

# 2. Buat script bot (main.py) dengan penanganan error yang kuat
RUN printf 'import telebot, os\n\
token = os.getenv("TOKEN")\n\
bot = telebot.TeleBot(token)\n\
@bot.message_handler(func=lambda m: True)\n\
def dl(m):\n\
    url = m.text\n\
    bot.reply_to(m, "Sabar, lagi download...")\n\
    try:\n\
        # Download video mp4 kualitas terbaik tanpa cookies\n\
        os.system(f"yt-dlp -f \"bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best\" --no-cookies -o vid.mp4 {url}")\n\
        with open("vid.mp4", "rb") as v: \n\
            bot.send_video(m.chat.id, v)\n\
        os.remove("vid.mp4")\n\
    except Exception as e:\n\
        bot.reply_to(m, f"Error: {e}")\n\
print("Bot sedang berjalan...")\n\
bot.infinity_polling()' > /app/main.py [cite: 2025-12-27]

# 3. Jalankan menggunakan Python secara langsung untuk menghindari error executable
CMD ["python", "/app/main.py"] [cite: 2025-12-27]
