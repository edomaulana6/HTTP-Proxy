"""
VidSave — Backend FastAPI + yt-dlp
Endpoint: POST /api/download
"""

import os
import uuid
import asyncio
from pathlib import Path

import yt_dlp
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, HttpUrl

# ─── Konfigurasi ────────────────────────────────────────────────────────────

DOWNLOAD_DIR = Path("downloads")
DOWNLOAD_DIR.mkdir(exist_ok=True)

app = FastAPI(title="VidSave API", version="1.0.0")

# Izinkan request dari browser (CORS)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],          # Ganti dengan domain kamu di production
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
    expose_headers=["X-Filename"],
)

# Sajikan file HTML statis (index.html)
if Path("static").exists():
    app.mount("/static", StaticFiles(directory="static"), name="static")


# ─── Model Request ──────────────────────────────────────────────────────────

class DownloadRequest(BaseModel):
    url: str
    format: str = "mp4"     # mp4 | mp3 | webm
    quality: str = "best"   # best | 1080 | 720 | 480 | 360


# ─── Helper: Build format string ────────────────────────────────────────────

def build_format_string(fmt: str, quality: str) -> str:
    if fmt == "mp3":
        return "bestaudio/best"

    height_map = {
        "1080": "1080",
        "720":  "720",
        "480":  "480",
        "360":  "360",
        "best": None,
    }
    height = height_map.get(quality)

    if height:
        return (
            f"bestvideo[height<={height}][ext=mp4]+bestaudio[ext=m4a]"
            f"/best[height<={height}][ext=mp4]"
            f"/best[height<={height}]"
        )
    return "bestvideo[ext=mp4]+bestaudio[ext=m4a]/bestvideo+bestaudio/best"


# ─── Endpoint utama ─────────────────────────────────────────────────────────

@app.post("/api/download")
async def download_video(req: DownloadRequest):
    """
    Terima URL video, download dengan yt-dlp, kembalikan file ke browser.
    """
    # Validasi platform
    allowed = ("youtube.com", "youtu.be", "tiktok.com")
    if not any(p in req.url for p in allowed):
        raise HTTPException(status_code=400, detail="Hanya mendukung YouTube dan TikTok.")

    # Nama file unik agar tidak tabrakan antar request
    session_id = uuid.uuid4().hex[:8]
    output_template = str(DOWNLOAD_DIR / f"{session_id}_%(title)s.%(ext)s")

    fmt_string = build_format_string(req.format, req.quality)

    ydl_opts: dict = {
        "format": fmt_string,
        "outtmpl": output_template,
        "merge_output_format": "mp4" if req.format != "mp3" else None,
        "noplaylist": True,
        "quiet": True,
        "no_warnings": True,
        "nocheckcertificate": True,
    }

    # Audio-only → konversi ke MP3
    if req.format == "mp3":
        ydl_opts["postprocessors"] = [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            }
        ]

    # Jalankan yt-dlp di thread terpisah agar tidak blokir event loop
    loop = asyncio.get_event_loop()
    try:
        filename = await loop.run_in_executor(None, _do_download, req.url, ydl_opts, session_id)
    except yt_dlp.utils.DownloadError as e:
        raise HTTPException(status_code=422, detail=f"Gagal download: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")

    if not filename or not Path(filename).exists():
        raise HTTPException(status_code=500, detail="File hasil download tidak ditemukan.")

    return FileResponse(
        path=filename,
        filename=Path(filename).name,
        media_type="application/octet-stream",
        headers={"X-Filename": Path(filename).name},
        background=_cleanup_task(filename),  # hapus file setelah dikirim
    )


def _do_download(url: str, ydl_opts: dict, session_id: str) -> str:
    """Download video dan kembalikan path file hasil."""
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        # Cari file yang sudah didownload berdasarkan session_id
        for f in DOWNLOAD_DIR.glob(f"{session_id}_*"):
            return str(f)
        # Fallback: ambil dari info dict
        return ydl.prepare_filename(info)


def _cleanup_task(filepath: str):
    """Background task: hapus file setelah response terkirim."""
    from starlette.background import BackgroundTask
    def delete():
        try:
            Path(filepath).unlink(missing_ok=True)
        except Exception:
            pass
    return BackgroundTask(delete)


# ─── Health check ────────────────────────────────────────────────────────────

@app.get("/api/health")
def health():
    return {"status": "ok", "message": "VidSave API berjalan ✅"}


@app.get("/")
def root():
    return {"message": "VidSave API — POST /api/download untuk download video."}
