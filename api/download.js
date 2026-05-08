// api/download.js
// Vercel Serverless Function — pakai Cobalt API (YouTube + TikTok)

export default async function handler(req, res) {
  // Hanya izinkan POST
  if (req.method !== 'POST') {
    return res.status(405).json({ detail: 'Method tidak diizinkan.' });
  }

  const { url, format = 'mp4', quality = '720' } = req.body;

  if (!url) {
    return res.status(400).json({ detail: 'URL tidak boleh kosong.' });
  }

  const allowed = ['youtube.com', 'youtu.be', 'tiktok.com'];
  if (!allowed.some(p => url.includes(p))) {
    return res.status(400).json({ detail: 'Hanya mendukung YouTube dan TikTok.' });
  }

  // Mapping kualitas ke format Cobalt
  const qualityMap = {
    'best': 'max',
    '1080': '1080',
    '720':  '720',
    '480':  '480',
    '360':  '360',
  };

  const cobaltQuality = qualityMap[quality] || '720';
  const isAudio = format === 'mp3';

  try {
    const cobaltRes = await fetch('https://api.cobalt.tools/api/json', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
      },
      body: JSON.stringify({
        url: url,
        vQuality: cobaltQuality,
        filenamePattern: 'basic',
        isAudioOnly: isAudio,
        aFormat: isAudio ? 'mp3' : undefined,
      }),
    });

    const data = await cobaltRes.json();

    // Cobalt mengembalikan status: stream / redirect / error / rate-limit
    if (data.status === 'error' || data.status === 'rate-limit') {
      return res.status(422).json({ detail: data.text || 'Gagal memproses video.' });
    }

    if (data.status === 'stream' || data.status === 'redirect' || data.status === 'tunnel') {
      // Kembalikan URL download ke frontend
      return res.status(200).json({ downloadUrl: data.url });
    }

    // Jika Cobalt langsung kasih picker (misal TikTok ada video+audio terpisah)
    if (data.status === 'picker') {
      const first = data.picker?.[0];
      if (first?.url) {
        return res.status(200).json({ downloadUrl: first.url });
      }
    }

    return res.status(500).json({ detail: 'Respons tidak dikenali dari server.' });

  } catch (err) {
    return res.status(500).json({ detail: 'Server error: ' + err.message });
  }
        }
        
