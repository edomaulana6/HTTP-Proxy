FROM python:3.10-slim

# 1. Install yt-dlp, ffmpeg, dan library bot telegram
RUN apt-get update && apt-get install -y ffmpeg && \
    pip install --no-cache-dir yt-dlp pyTelegramBotAPI

WORKDIR /app

# 2. SC Bot Telegram Sederhana (Download & Kirim Video)
RUN echo 'import telebot, os; \
bot = telebot.TeleBot("TOKEN_BOT_ANDA"); \
@bot.message_handler(func=lambda m: True) \
def dl(m): \
    url = m.text; \
    bot.reply_to(m, "Sabar, lagi download..."); \
    os.system(f"yt-dlp -f \"bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best\" --no-cookies -o vid.mp4 {url}"); \
    with open("vid.mp4", "rb") as v: bot.send_video(m.chat.id, v); \
    os.remove("vid.mp4"); \
bot.infinity_polling()' > bot.py

CMD ["python", "bot.py"]
