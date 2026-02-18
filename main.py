import telebot
import os
import time
import threading

# Masukkan token Anda di dalam tanda kutip di bawah ini secara teliti
TOKEN = "MASUKKAN_TOKEN_DISINI"

try:
    bot = telebot.TeleBot(TOKEN)
    print("LOG: Sistem otentikasi berhasil.")
except Exception as e:
    print(f"LOG ERROR: Masalah pada kredensial: {e}")

# RESET MEMORY: Fitur penghapusan otomatis setiap 1 menit (60 detik)
def auto_clean():
    while True:
        time.sleep(60)
        for f in os.listdir("."):
            if f.endswith((".mp4", ".webm", ".mkv")):
                try:
                    os.remove(f)
                except:
                    pass

# Jalankan pembersihan memori di latar belakang
threading.Thread(target=auto_clean, daemon=True).start()

@bot.message_handler(func=lambda m: m.text.startswith("http"))
def handle_download(m):
    bot.reply_to(m, "Sabar, video sedang diproses...")
    try:
        out = f"v_{m.chat.id}.mp4"
        # Download video dengan yt-dlp
        os.system(f'yt-dlp -f "best" --no-cookies -o "{out}" "{m.text}"')
        if os.path.exists(out):
            with open(out, "rb") as v:
                bot.send_video(m.chat.id, v)
            os.remove(out) # Langsung hapus setelah terkirim
    except Exception as e:
        bot.reply_to(m, f"Terjadi kendala teknis: {e}")

print("BOT AKTIF SEKARANG!")
bot.infinity_polling()
