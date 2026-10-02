from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os, json, datetime
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_groq import ChatGroq
from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

load_dotenv(override=True)
app = FastAPI(title="ManifestAI Pro API")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

HISTORY_FILE = "history.json"

class ContentRequest(BaseModel):
    topic: str; brand_name: str; goal: str; target_audience: str; persona: str; expertise: str
    content_type: str; tone: str; length: str; output_format: str
    keywords: str; words_to_avoid: str; emojis: str; hashtags: str; cta: str; creativity: float
    variations: int = 1
    save_history: bool = False

def validate_content(content, content_type, include_hashtags, cta_choice):
    status_messages = []
    if include_hashtags == "Yes" and "#" not in content:
        content += "\n\n#Trending #Innovation #ManifestAI"
        status_messages.append("Added Missing Hashtags")
    if cta_choice != "None" and not any(w in content.lower() for w in ["click", "scan", "hurry", "subscribe", "book", "reply", "comment"]):
        content += f"\n\n👉 {cta_choice}"
        status_messages.append("Added Missing CTA")
    if content_type == "Professional Email" and "Subject:" not in content:
        content = "Subject: Important Update\n\n" + content
        status_messages.append("Added Subject Line")
    return content, "⚠️ Fixed: " + ", ".join(status_messages) if status_messages else "✅ Passed Checks"

def analyze_text(text, target_keywords):
    words = text.split()
    word_count = len(words)
    pos_score = sum(1 for w in words if w.lower().strip('.,!?') in {'great', 'excellent', 'happy', 'success', 'growth', 'best', 'innovative', 'vision'})
    neg_score = sum(1 for w in words if w.lower().strip('.,!?') in {'bad', 'terrible', 'fail', 'worst', 'hard', 'difficult', 'issue', 'problem', 'risk'})

    if pos_score > neg_score: sentiment = "Positive 🟢"
    elif neg_score > pos_score: sentiment = "Negative 🔴"
    else: sentiment = "Neutral ⚪"

    sentences = max(text.count('.') + text.count('!') + text.count('?'), 1)
    wps = word_count / sentences
    readability = "Easy" if wps < 12 else ("Advanced" if wps > 20 else "Standard")

    kw_found = 0
    if target_keywords and target_keywords.lower() != "none":
        kws = [k.strip().lower() for k in target_keywords.split(',')]
        kw_found = sum(1 for k in kws if k in text.lower())

    return {"word_count": word_count, "sentiment": sentiment, "readability": readability, "keywords_found": kw_found}

def save_to_history(req, output, engine):
    entry = {
        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "topic": req.topic, "type": req.content_type,
        "audience": req.target_audience, "engine": engine, "output": output
    }
    history = []
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r") as f:
            try: history = json.load(f)
            except: pass
    history.insert(0, entry)
    with open(HISTORY_FILE, "w") as f: json.dump(history[:50], f, indent=4)

@app.get("/api/history")
async def get_history():
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r") as f: return json.load(f)
    return []

# --- NEW: Task 2.4/2.5 Clear History Endpoint ---
@app.delete("/api/history")
async def clear_history():
    with open(HISTORY_FILE, "w") as f: json.dump([], f)
    return {"status": "History Cleared"}

@app.post("/api/generate")
async def generate_content(req: ContentRequest):
    try:
        llm_gemini = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=req.creativity, api_key=os.getenv("GOOGLE_API_KEY"))
        llm_groq = ChatGroq(model="llama-3.3-70b-versatile", temperature=req.creativity, api_key=os.getenv("GROQ_API_KEY"))
        llm_ollama = ChatOllama(model="llama3.2:1b", temperature=req.creativity)

        template = """
        BRAND: {brand_name} | GOAL: {goal}
        AUDIENCE: {target_audience} (Level: {expertise}) | PERSONA: {persona}
        TYPE: {content_type} | COMBINED TONES: {tone} | FORMAT: {output_format} | LENGTH: {length}
        KEYWORDS: {keywords} | AVOID: {words_to_avoid}
        RULES: Emojis: {emojis}, Hashtags: {hashtags}, Required CTA: {cta}

        TOPIC: {topic}
        INSTRUCTIONS: Generate the {content_type}. Blend the requested COMBINED TONES. Use {output_format}. If Emojis Allowed is 'No', DO NOT use emojis.
        """
        prompt = ChatPromptTemplate.from_template(template)

        outputs = []
        metrics_list = []
        statuses = []
        used_engine = "ManifestAI Core ✨"

        for i in range(req.variations):
            current_creativity = req.creativity if i == 0 else min(req.creativity + 0.2, 1.0)
            chain_inputs = req.dict()

            try:
                llm_gemini.temperature = current_creativity
                raw_response = (prompt | llm_gemini | StrOutputParser()).invoke(chain_inputs)
            except:
                try:
                    llm_groq.temperature = current_creativity
                    raw_response = (prompt | llm_groq | StrOutputParser()).invoke(chain_inputs)
                except:
                    llm_ollama.temperature = current_creativity
                    raw_response = (prompt | llm_ollama | StrOutputParser()).invoke(chain_inputs)

            final_output, val_status = validate_content(raw_response, req.content_type, req.hashtags, req.cta)
            metrics = analyze_text(final_output, req.keywords)

            outputs.append(final_output)
            metrics_list.append(metrics)
            statuses.append(val_status)

        if req.save_history:
            save_to_history(req, outputs[0], used_engine)

        return {"outputs": outputs, "statuses": statuses, "engine": used_engine, "metrics": metrics_list}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))