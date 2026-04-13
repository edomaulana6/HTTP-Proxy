export async function onRequestPost(context) {
  const { request, env } = context;
  const { text } = await request.json();

  let baseScore = 0;

  // Logika skor dasar Anda
  if (text.length > 20) baseScore += 20;
  if (/\d/.test(text)) baseScore += 20;
  if (text.toLowerCase().includes("rahasia")) baseScore += 20;
  if (text.includes("!") || text.includes("?")) baseScore += 10;

  const response = await fetch("https://api.openai.com/v1/chat/completions", {
    method: "POST",
    headers: {
      "Authorization": `Bearer ${env.OPENAI_API_KEY}`,
      "Content-Type": "application/json"
    },
    body: JSON.stringify({
      model: "gpt-4o-mini",
      messages: [
        { role: "system", content: "You are an expert viral hook analyzer." },
        {
          role: "user",
          content: `Analisa hook dan beri skor 0-50 dalam JSON:
          { "score": number, "feedback": "string" }
          Hook: "${text}"`
        }
      ]
    })
  });

  const data = await response.json();

  let aiData;
  try {
    aiData = JSON.parse(data.choices[0].message.content);
  } catch {
    aiData = { score: 25, feedback: "Gagal memproses data AI, menggunakan fallback." };
  }

  // Penggabungan skor dasar dan AI, batas maksimal 100
  const finalScore = Math.min(100, baseScore + aiData.score);

  return new Response(JSON.stringify({
    score: finalScore,
    feedback: aiData.feedback
  }), {
    headers: { "Content-Type": "application/json" }
  });
    }
  
