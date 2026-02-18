import telebot
import os
import time
import threading

# Pastikan Nama Variabel di Koyeb adalah TOKEN
TOKEN = os.getenv("TOKEN")
if not TOKEN:
    print("ERROR: Variabel TOKEN tidak ditemukan di Koyeb!")
    exit(1)

bot = telebot.TeleBot(TOKEN)

# Reset Memori: Hapus file video setiap 1 menit
def auto_clean():
    while True:
        time.sleep(60)
        for f in os.listdir("."):
            if f.endswith((".mp4", ".webm", ".mkv")):
                try:
                    os.remove(f)
                    print(f"Pembersihan otomatis: {f} dihapus")
                except Exception as e:
                    print(f"Gagal hapus {f}: {e}")

threading.Thread(target=auto_clean, daemon=True).start()

@bot.message_handler(func=lambda m: True)
def dl(m):
    if not m.text.startswith("http"):
        return
    
    bot.reply_to(m, "Sabar, lagi download...")
    try:
        # Nama file unik
        out = f"video_{m.chat.id}.mp4"
        # Download pakai yt-dlp
        status = os.system(f'yt-dlp -f "best" --no-cookies -o "{out}" "{m.text}"')
        
        if status == 0 and os.path.exists(out):
            with open(out, "rb") as v:
                bot.send_video(m.chat.id, v)
            os.remove(out)
        else:
            bot.reply_to(m, "Gagal download. Link tidak valid atau server sibuk.")
    except Exception as e:
        bot.reply_to(m, f"Error: {e}")

print("Bot Jalan...")
bot.infinity_polling()
