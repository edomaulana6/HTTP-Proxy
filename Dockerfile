FROM python:3.10-slim

RUN apt-get update && apt-get install -y ffmpeg && \
    pip install --no-cache-dir yt-dlp pyTelegramBotAPI

WORKDIR /app

# Script Python yang membaca variable 'TOKEN' dari Koyeb
RUN echo 'import telebot, os; \
token = os.getenv("TOKEN"); \
bot = telebot.TeleBot(token); \
@bot.message_handler(func=lambda m: True) \
def dl(m): \
    url = m.text; \
    bot.reply_to(m, "Sabar, lagi download..."); \
    try: \
        os.system(f"yt-dlp -f \"bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best\" --no-cookies -o vid.mp4 {url}"); \
        with open("vid.mp4", "rb") as v: bot.send_video(m.chat.id, v); \
        os.remove("vid.mp4"); \
    except Exception as e: bot.reply_to(m, f"Error: {e}"); \
bot.infinity_polling()' > bot.py

CMD ["python", "bot.py"]
