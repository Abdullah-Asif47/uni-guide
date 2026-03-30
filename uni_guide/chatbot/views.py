import os
from groq import Groq
from django.shortcuts import render
from dotenv import load_dotenv

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

SYSTEM_PROMPT = """You are a knowledgeable and empathetic university guidance counselor 
for Pakistani students. You have deep knowledge of Pakistani universities including NUST, 
FAST, LUMS, COMSATS, UET, GIKI, IBA, SZABIST, UCP, and Virtual University.

Rules:
- Give specific, actionable advice — not vague "check the website" answers
- When asked about merit, give the most recent known ranges with context
- When a student seems stressed or confused, acknowledge their feelings first
- Recommend 2-3 realistic options based on their situation, not just top universities
- If asked in Urdu, respond in Urdu. If English, respond in English
- Never answer unrelated questions — redirect warmly back to university guidance
- NEVER tell jokes or engage in humor under any circumstances. If asked, say: 'I'm only here to help with university guidance. 
    What's your situation?'
- Always end with one specific follow-up question to understand their situation better
- Keep responses under 150 words. Be direct. No bullet point walls. Students are stressed and on mobile.

Remember: Many Pakistani students have no one to guide them. You are often their 
only source of honest advice. Be specific, be real, be helpful."""

def chat_view(request):
    if 'history' not in request.session:
        request.session['history'] = []

    if request.method == 'POST':
        user_input = request.POST.get('message', '').strip()
        if not user_input:
            return render(request, 'chatbot/chat.html', {'history': request.session.get('history', [])})

        history = request.session['history']

        messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        for msg in history[-5:]:
            messages.append({"role": "user", "content": msg['user']})
            messages.append({"role": "assistant", "content": msg['bot']})
        messages.append({"role": "user", "content": user_input})

        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages,
            max_tokens=1024
        )

        response_text = response.choices[0].message.content
        history.append({'user': user_input, 'bot': response_text})
        request.session['history'] = history
        request.session.modified = True

    return render(request, 'chatbot/chat.html', {
        'history': request.session.get('history', [])
    })