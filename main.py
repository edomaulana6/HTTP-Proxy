import telebot
import os
import time
import threading

# Ambil TOKEN dari Environment Variable Koyeb
TOKEN = os.getenv("TOKEN")
bot = telebot.TeleBot(TOKEN)

# Fungsi pembersihan memori setiap 1 menit
def auto_clean():
    while True:
        time.sleep(60)
        for file in os.listdir("."):
            # Hapus file video yang tersisa
            if file.endswith((".mp4", ".webm", ".mkv")):
                try:
                    os.remove(file)
                    print(f"Pembersihan otomatis: {file} dihapus")
                except:
                    pass

# Jalankan pembersih di background
threading.Thread(target=auto_clean, daemon=True).start()

@bot.message_handler(func=lambda m: True)
def handle_download(m):
    url = m.text
    if not url.startswith("http"):
        return
        
    bot.reply_to(m, "Sabar, lagi download...")
    try:
        # Download video mp4 kualitas terbaik
        cmd = f'yt-dlp -f "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best" --no-cookies -o "hasil_video.mp4" "{url}"'
        os.system(cmd)
        
        if os.path.exists("hasil_video.mp4"):
            with open("hasil_video.mp4", "rb") as video:
                bot.send_video(m.chat.id, video)
            os.remove("hasil_video.mp4")
        else:
            bot.reply_to(m, "Gagal ambil video. Link mungkin salah atau sedang gangguan.")
    except Exception as e:
        bot.reply_to(m, f"Error: {e}")

print("Bot Aktif & Auto-clean Jalan...")
bot.infinity_polling()
