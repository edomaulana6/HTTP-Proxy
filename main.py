import telebot
import os
import time
import threading

# Ambil token dari Environment Variable Koyeb
token = os.getenv("TOKEN")
bot = telebot.TeleBot(token)

# Fungsi pembersih memory (file video) setiap 1 menit
def cleaner():
    while True:
        time.sleep(60)
        for f in os.listdir("."):
            if f.endswith((".mp4", ".webm", ".mkv")):
                try:
                    os.remove(f)
                    print(f"Auto-clean: {f} dihapus")
                except:
                    pass

# Jalankan cleaner di background
threading.Thread(target=cleaner, daemon=True).start()

@bot.message_handler(func=lambda m: True)
def dl(m):
    url = m.text
    bot.reply_to(m, "Sabar, lagi download...")
    try:
        # Download kualitas terbaik
        os.system(f'yt-dlp -f "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best" --no-cookies -o vid.mp4 {url}')
        
        if os.path.exists("vid.mp4"):
            with open("vid.mp4", "rb") as v:
                bot.send_video(m.chat.id, v)
            os.remove("vid.mp4")
        else:
            bot.reply_to(m, "Gagal mengunduh video. Pastikan link benar.")
    except Exception as e:
        bot.reply_to(m, f"Error: {e}")

print("Bot Jalan & Auto-clean Aktif (1 Menit)...")
bot.infinity_polling()
