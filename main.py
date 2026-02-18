import telebot
import os
import time
import threading

# GANTI bagian di bawah ini dengan token asli Anda yang tadi
TOKEN = "MASUKKAN_TOKEN_ANDA_DI_SINI" 
bot = telebot.TeleBot(TOKEN)

# RESET MEMORY: Hapus file video setiap 1 menit secara otomatis
def auto_clean():
    while True:
        time.sleep(60)
        for f in os.listdir("."):
            # Target file video agar penyimpanan tidak penuh
            if f.endswith((".mp4", ".webm", ".mkv")):
                try:
                    os.remove(f)
                    print(f"Auto-clean: {f} berhasil dihapus dari memori.")
                except:
                    pass

# Jalankan cleaner di latar belakang
threading.Thread(target=auto_clean, daemon=True).start()

@bot.message_handler(func=lambda m: True)
def handle_download(m):
    if not m.text.startswith("http"):
        return
        
    bot.reply_to(m, "Sabar ya, video sedang diproses...")
    
    # Nama file unik berdasarkan ID chat
    file_output = f"vid_{m.chat.id}.mp4"
    
    try:
        # Perintah download yang paling stabil
        os.system(f'yt-dlp -f "best" --no-cookies -o "{file_output}" "{m.text}"')
        
        if os.path.exists(file_output):
            with open(file_output, "rb") as video:
                bot.send_video(m.chat.id, video)
            os.remove(file_output) # Hapus setelah dikirim
        else:
            bot.reply_to(m, "Gagal ambil video. Link salah atau server lagi sibuk.")
    except Exception as e:
        bot.reply_to(m, f"Error sistem: {e}")

print("BOT AKTIF SEKARANG!")
bot.infinity_polling()
