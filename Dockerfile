FROM python:3.10-slim

# Install ffmpeg dan library pendukung
RUN apt-get update && apt-get install -y ffmpeg && \
    pip install --no-cache-dir yt-dlp pyTelegramBotAPI

WORKDIR /app

# Membuat script bot langsung di dalam container agar pasti ditemukan
RUN echo 'import telebot, os, time, threading \n\
TOKEN = os.getenv("TOKEN") \n\
bot = telebot.TeleBot(TOKEN) \n\
def auto_clean(): \n\
    while True: \n\
        time.sleep(60) \n\
        for f in os.listdir("."): \n\
            if f.endswith((".mp4", ".webm", ".mkv")): \n\
                try: os.remove(f) \n\
                except: pass \n\
threading.Thread(target=auto_clean, daemon=True).start() \n\
@bot.message_handler(func=lambda m: True) \n\
def dl(m): \n\
    if not m.text.startswith("http"): return \n\
    bot.reply_to(m, "Sabar, lagi download...") \n\
    try: \n\
        os.system(f"yt-dlp -f \"bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best\" --no-cookies -o vid.mp4 {m.text}") \n\
        with open("vid.mp4", "rb") as v: bot.send_video(m.chat.id, v) \n\
        if os.path.exists("vid.mp4"): os.remove("vid.mp4") \n\
    except Exception as e: bot.reply_to(m, f"Error: {e}") \n\
print("Bot Jalan...") \n\
bot.infinity_polling()' > bot.py

# Jalankan dengan memanggil python secara eksplisit
CMD ["python", "bot.py"]
