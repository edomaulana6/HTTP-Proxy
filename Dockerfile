FROM python:3.10-slim

RUN apt-get update && apt-get install -y ffmpeg && \
    pip install --no-cache-dir yt-dlp pyTelegramBotAPI

WORKDIR /app

RUN printf 'import telebot, os, time, threading\n\
token = os.getenv("TOKEN")\n\
bot = telebot.TeleBot(token)\n\
\n\
def cleaner():\n\
    while True:\n\
        time.sleep(60)\n\
        for f in os.listdir("."):\n\
            if f.endswith(".mp4") or f.endswith(".webm") or f.endswith(".mkv"):\n\
                try: os.remove(f); print(f"Auto-clean: {f} dihapus")\n\
                except: pass\n\
\n\
threading.Thread(target=cleaner, daemon=True).start()\n\
\n\
@bot.message_handler(func=lambda m: True)\n\
def dl(m):\n\
    url = m.text\n\
    bot.reply_to(m, "Sabar, lagi download...")\n\
    try:\n\
        os.system(f"yt-dlp -f \"bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best\" --no-cookies -o vid.mp4 {url}")\n\
        with open("vid.mp4", "rb") as v: bot.send_video(m.chat.id, v)\n\
        if os.path.exists("vid.mp4"): os.remove("vid.mp4")\n\
    except Exception as e: bot.reply_to(m, f"Error: {e}")\n\
\n\
print("Bot Jalan & Auto-clean Aktif (1 Menit)...")\n\
bot.infinity_polling()' > /app/main.py

CMD ["python", "/app/main.py"]
