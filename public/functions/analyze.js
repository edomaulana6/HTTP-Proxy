export async function onRequestPost(context) {
  const { request, env } = context;

  // VALIDASI INPUT
  let body;
  try {
    body = await request.json();
  } catch {
    return new Response("Invalid JSON", { status: 400 });
  }

  const text = body.text || "";

  // RULE BASE
  let baseScore = 0;
  if (text.length > 20) baseScore += 20;
  if (/\d/.test(text)) baseScore += 20;
  if (text.toLowerCase().includes("rahasia")) baseScore += 20;
  if (text.includes("!") || text.includes("?")) baseScore += 10;

  // CEK API KEY
  if (!env.OPENAI_API_KEY) {
    return new Response(JSON.stringify({
      score: baseScore,
      feedback: "API key belum diset"
    }), {
      headers: { "Content-Type": "application/json" }
    });
  }

  // REQUEST KE OPENAI
  let aiScore = 25;
  let feedback = "fallback";

  try {
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
        ],
        temperature: 0.7
      })
    });

    const data = await response.json();

    // VALIDASI RESPONSE OPENAI
    if (data.choices && data.choices.length > 0) {
      try {
        const parsed = JSON.parse(data.choices[0].message.content);
        aiScore = parsed.score || 25;
        feedback = parsed.feedback || "no feedback";
      } catch {
        feedback = data.choices[0].message.content;
      }
    } else {
      feedback = "AI tidak merespon";
    }

  } catch (err) {
    feedback = "Error koneksi AI";
  }

  const finalScore = Math.min(100, baseScore + aiScore);

  return new Response(JSON.stringify({
    score: finalScore,
    feedback
  }), {
    headers: { "Content-Type": "application/json" }
  });
}
