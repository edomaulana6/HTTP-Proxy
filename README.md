# 🎬 VidSave — Video Downloader

Download video YouTube & TikTok via website. Frontend HTML + Backend FastAPI + yt-dlp.

---

## 📁 Struktur Project

```
vidsave/
├── server.py           ← Backend FastAPI (file ini)
├── requirements.txt    ← Daftar library Python
├── index.html          ← Frontend website (taruh di root atau folder static/)
└── downloads/          ← Folder sementara (dibuat otomatis)
```

---

## ⚡ Cara Instalasi & Menjalankan

### 1. Install dependensi Python

```bash
pip install -r requirements.txt
```

### 2. Install FFmpeg (wajib untuk merge video+audio)

| OS | Perintah |
|---|---|
| Windows | Download dari https://ffmpeg.org, tambahkan ke PATH |
| macOS | `brew install ffmpeg` |
| Ubuntu/Debian | `sudo apt install ffmpeg` |

### 3. Jalankan server

```bash
uvicorn server:app --reload --port 8000
```

Server berjalan di: http://localhost:8000

### 4. Buka website

Buka `index.html` di browser. Pastikan file `index.html` ada di folder yang sama.
Atau akses langsung API-nya di: http://localhost:8000/docs

---

## 🔌 Endpoint API

### POST /api/download

Download video dan kembalikan file ke browser.

**Request Body (JSON):**
```json
{
  "url": "https://www.youtube.com/watch?v=xxxxx",
  "format": "mp4",
  "quality": "720"
}
```

| Field | Nilai | Keterangan |
|---|---|---|
| `url` | string | URL YouTube atau TikTok |
| `format` | `mp4` / `mp3` / `webm` | Format output |
| `quality` | `best` / `1080` / `720` / `480` / `360` | Resolusi video |

**Response:** File binary (video/audio) langsung diunduh browser.

---

### GET /api/health

Cek apakah server berjalan.

```json
{ "status": "ok", "message": "VidSave API berjalan ✅" }
```

---

## 🌐 Deploy ke Server (opsional)

Untuk deploy ke VPS/cloud:

```bash
uvicorn server:app --host 0.0.0.0 --port 8000
```

Gunakan Nginx sebagai reverse proxy dan ganti `allow_origins=["*"]`
dengan domain spesifik kamu di bagian CORSMiddleware di `server.py`.
