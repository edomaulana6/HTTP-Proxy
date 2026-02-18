import telebot
import os
import time
import threading

# Mengambil Token dari Environment Variable Koyeb
TOKEN = os.getenv("TOKEN")
bot = telebot.TeleBot(TOKEN)

# Fungsi membersihkan file video setiap 1 menit
def auto_clean():
    while True:
        time.sleep(60)
        for file in os.listdir("."):
            if file.endswith((".mp4", ".webm", ".mkv")):
                try:
                    os.remove(file)
                    print(f"Pembersihan otomatis: {file} dihapus")
                except Exception as e:
                    print(f"Gagal menghapus {file}: {e}")

# Jalankan fungsi pembersih di latar belakang
threading.Thread(target=auto_clean, daemon=True).start()

@bot.message_handler(func=lambda m: True)
def handle_download(m):
    url = m.text
    bot.reply_to(m, "Sabar, sedang mengunduh video...")
    try:
        # Perintah download yt-dlp (MP4 kualitas terbaik tanpa cookies)
        os.system(f'yt-dlp -f "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best" --no-cookies -o video_hasil.mp4 "{url}"')
        
        if os.path.exists("video_hasil.mp4"):
            with open("video_hasil.mp4", "rb") as video:
                bot.send_video(m.chat.id, video)
            os.remove("video_hasil.mp4")
        else:
            bot.reply_to(m, "Gagal mengunduh. Link tidak didukung atau YouTube sedang error.")
    except Exception as e:
        bot.reply_to(m, f"Terjadi kesalahan: {e}")

print("Bot Telegram Aktif & Pembersih 1 Menit Berjalan...")
bot.infinity_polling()
