import streamlit as st
import os, json, datetime
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_groq import ChatGroq
from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

st.set_page_config(page_title="ManifestAI Engine PRO", page_icon="🚀", layout="wide")

PREFS_FILE = "prefs.json"
HISTORY_FILE = "history.json"

def load_prefs():
    if os.path.exists(PREFS_FILE):
        with open(PREFS_FILE, "r") as f:
            try: return json.load(f)
            except: pass
    return {}

def save_prefs(prefs_dict):
    with open(PREFS_FILE, "w") as f: json.dump(prefs_dict, f)
    st.sidebar.success("✅ Profile Saved!")

user_prefs = load_prefs()

def analyze_text(text, target_keywords):
    words = text.split()
    word_count = len(words)
    pos_score = sum(1 for w in words if w.lower().strip('.,!?') in {'great', 'excellent', 'happy', 'success', 'growth', 'best', 'innovative'})
    neg_score = sum(1 for w in words if w.lower().strip('.,!?') in {'bad', 'terrible', 'fail', 'worst', 'hard', 'issue', 'problem', 'risk'})
    sentiment = "Positive 🟢" if pos_score > neg_score else "Negative 🔴" if neg_score > pos_score else "Neutral ⚪"
    wps = word_count / max(text.count('.') + text.count('!') + text.count('?'), 1)
    readability = "Easy" if wps < 12 else ("Advanced" if wps > 20 else "Standard")
    kw_found = sum(1 for k in target_keywords.split(',') if k.strip().lower() in text.lower()) if target_keywords and target_keywords.lower() != "none" else 0
    return word_count, sentiment, readability, kw_found

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

with st.sidebar:
    st.title("🎛️ Content Control Panel")

    audience_options = ["Corporate Executives / B2B", "Tech-Savvy Millennials", "Gen Z Consumers", "Small Business Owners", "Job Seekers", "Investors & VCs", "Existing Customers", "Students & Graduates", "Healthcare Professionals", "General Public", "Other (Type Manual)"]
    persona_options = ["Corporate CEO", "Marketing Expert", "Software Engineer", "HR Manager", "Sales Representative", "Industry Thought Leader", "Customer Support", "Freelancer", "Other (Type Manual)"]
    goal_options = ["Sales/Conversion", "Lead Generation", "Brand Awareness", "Engagement & Community", "Educational / Value Add", "Thought Leadership", "Apology / Crisis Management", "Event Promotion"]
    content_options = ["LinkedIn Post", "Professional Email", "Ad Copy", "Twitter Thread", "Blog Post", "Press Release"]
    tone_options = ["Professional", "Engaging", "Persuasive", "Casual", "Urgent", "Empathetic", "Witty", "Authoritative", "Inspirational", "Data-Driven", "Other (Type Manual)"]
    format_options = ["Plain Text", "Bullet Points", "Markdown", "Numbered List", "Formal Letter", "Script / Dialogue"]
    cta_options = ["None", "Share your thoughts in the comments 👇", "Click the link to learn more 🔗", "Hurry up! Limited time offer ⏳", "Book a Demo today 📅", "Reply to this email ✉️", "Subscribe for more updates 🔔", "Other (Type Manual)"]

    st.header("1. Strategy & Goal")
    content_type = st.selectbox("Content Type:", content_options)

    def_aud = 0; def_per = 0; def_goal = 0; def_tone = ["Professional"]; def_fmt = 0; def_emj = 0; def_hash = 0; def_cta = 0
    if content_type == "LinkedIn Post":
        def_aud = audience_options.index("Corporate Executives / B2B"); def_per = persona_options.index("Industry Thought Leader"); def_goal = goal_options.index("Thought Leadership"); def_tone = ["Engaging"]; def_fmt = format_options.index("Bullet Points"); def_cta = cta_options.index("Share your thoughts in the comments 👇")
    elif content_type == "Professional Email":
        def_aud = audience_options.index("Existing Customers"); def_per = persona_options.index("Sales Representative"); def_goal = goal_options.index("Lead Generation"); def_tone = ["Professional"]; def_fmt = format_options.index("Formal Letter"); def_emj = 1; def_hash = 1; def_cta = cta_options.index("Reply to this email ✉️")
    elif content_type == "Ad Copy":
        def_aud = audience_options.index("Gen Z Consumers"); def_per = persona_options.index("Marketing Expert"); def_goal = goal_options.index("Sales/Conversion"); def_tone = ["Persuasive"]; def_fmt = format_options.index("Plain Text"); def_emj = 0; def_hash = 1; def_cta = cta_options.index("Click the link to learn more 🔗")

    if user_prefs:
        try:
            if user_prefs.get('goal') in goal_options: def_goal = goal_options.index(user_prefs['goal'])
            if user_prefs.get('audience') in audience_options: def_aud = audience_options.index(user_prefs['audience'])
            if user_prefs.get('persona') in persona_options: def_per = persona_options.index(user_prefs['persona'])
        except: pass

    goal = st.selectbox("Primary Goal:", goal_options, index=def_goal)
    brand_name = st.text_input("Brand Name (Optional):", value=user_prefs.get('brand', ''))

    st.header("2. Audience & Voice")
    sel_aud = st.selectbox("Target Audience:", audience_options, index=def_aud)
    final_aud = st.text_input("Custom Audience:", "Local Shoppers") if sel_aud == "Other (Type Manual)" else sel_aud

    sel_per = st.selectbox("Author Persona:", persona_options, index=def_per)
    final_per = st.text_input("Custom Persona:", "Fitness Coach") if sel_per == "Other (Type Manual)" else sel_per

    expertise_level = st.select_slider("Audience Expertise Level:", options=["Beginner", "Intermediate", "Expert"], value="Intermediate")

    st.header("3. Tone & Formatting")
    sel_tones = st.multiselect("Tone (Select Multiple):", tone_options, default=def_tone)
    final_tones = []
    for t in sel_tones:
        if t == "Other (Type Manual)": final_tones.append(st.text_input("Custom Tone:", "Cinematic"))
        else: final_tones.append(t)
    tones_str = ", ".join(final_tones) if final_tones else "Professional"

    output_format = st.selectbox("Output Format:", format_options, index=def_fmt)
    length = st.select_slider("Length:", options=["Short (Tweet)", "Medium (Paragraph)", "Long (Article)"], value="Medium (Paragraph)")

    col1, col2 = st.columns(2)
    with col1: include_emojis = st.radio("Emojis?", ["Yes", "No"], index=def_emj)
    with col2: include_hashtags = st.radio("Hashtags?", ["Yes", "No"], index=def_hash)

    sel_cta = st.selectbox("Call to Action (CTA):", cta_options, index=def_cta)
    final_cta = st.text_input("Custom CTA:", "Buy now!") if sel_cta == "Other (Type Manual)" else sel_cta

    st.header("4. Constraints & Modes")
    keywords = st.text_input("Keywords to Include:", placeholder="e.g., AI, ROI")
    words_to_avoid = st.text_input("Words to Avoid:", placeholder="e.g., cheap, spam")
    creativity = st.slider("Creativity Level:", 0.0, 1.0, 0.7)

    compare_mode = st.checkbox("Generate 2 Variations (Compare Mode)")
    save_to_hist = st.checkbox("💾 Log to Version History", value=False)

    if st.button("💾 Save User Profile Defaults"):
        save_prefs({"brand": brand_name, "goal": goal, "audience": final_aud, "persona": final_per})

tab_gen, tab_hist = st.tabs(["✨ Content Generator", "📜 Version History"])

with tab_gen:
    st.title("🚀 ManifestAI Engine PRO")
    topic_text = st.text_area("👇 Enter Topic or Raw Text:", height=150)

    if st.button("✨ Manifest Content", type="primary"):
        if not topic_text: st.warning("Please enter a topic first."); st.stop()

        load_dotenv(override=True)
        llm_gemini = ChatGoogleGenerativeAI(model="gemini-2.5-flash", api_key=os.getenv("GOOGLE_API_KEY"))
        llm_groq = ChatGroq(model="llama-3.3-70b-versatile", api_key=os.getenv("GROQ_API_KEY"))
        llm_ollama = ChatOllama(model="llama3.2:1b")

        template = """BRAND: {brand} | GOAL: {goal}
        AUDIENCE: {aud} (Level: {exp}) | PERSONA: {per}
        TYPE: {type} | TONE: {tone} | FORMAT: {fmt} | LENGTH: {len}
        KEYWORDS: {kw} | AVOID: {avoid}
        RULES: Emojis: {emj}, Hashtags: {hash}, CTA: {cta}
        TOPIC: {topic}
        INSTRUCTIONS: Generate the {type}. Blend the requested TONE perfectly. Strictly use {fmt}. Avoid WORDS TO AVOID. If Emojis 'No', use ZERO emojis."""
        prompt = ChatPromptTemplate.from_template(template)

        inputs = {
            "topic": topic_text, "brand": brand_name or "Generic", "goal": goal, "aud": final_aud,
            "per": final_per, "exp": expertise_level, "type": content_type, "tone": tones_str,
            "fmt": output_format, "len": length, "kw": keywords or "None", "avoid": words_to_avoid or "None",
            "emj": include_emojis, "hash": include_hashtags, "cta": final_cta
        }

        variations = 2 if compare_mode else 1
        outputs = []
        used_engine = "ManifestAI Core ✨"

        with st.spinner("⚙️ Manifesting..."):
            for i in range(variations):
                current_temp = creativity if i == 0 else min(creativity + 0.2, 1.0)
                try:
                    llm_gemini.temperature = current_temp; raw = (prompt | llm_gemini | StrOutputParser()).invoke(inputs)
                except:
                    try: llm_groq.temperature = current_temp; raw = (prompt | llm_groq | StrOutputParser()).invoke(inputs)
                    except: llm_ollama.temperature = current_temp; raw = (prompt | llm_ollama | StrOutputParser()).invoke(inputs)

                final_out, val_status = validate_content(raw, content_type, include_hashtags, final_cta)
                outputs.append((final_out, val_status))

        st.session_state['generated_outputs'] = outputs
        st.session_state['used_engine'] = used_engine
        st.session_state['topic_used'] = topic_text

        if save_to_hist:
            hist = []
            if os.path.exists(HISTORY_FILE):
                with open(HISTORY_FILE, "r") as f:
                    try: hist = json.load(f)
                    except: pass
            hist.insert(0, {"timestamp": str(datetime.datetime.now())[:16], "type": content_type, "topic": topic_text[:50], "engine": used_engine, "output": outputs[0][0]})
            with open(HISTORY_FILE, "w") as f: json.dump(hist[:50], f)

    if 'generated_outputs' in st.session_state:
        outputs = st.session_state['generated_outputs']
        used_engine = st.session_state['used_engine']

        words, sent, read, kw_found = analyze_text(outputs[0][0], keywords)
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Word Count", words); m2.metric("Sentiment", sent); m3.metric("Readability", read); m4.metric("Keywords Found", kw_found)

        st.success(f"✨ Manifestation Complete! Engine: {used_engine}")

        if len(outputs) > 1:
            c1, c2 = st.columns(2)
            with c1:
                st.info(f"🛡️ Var 1 Validation: {outputs[0][1]}")
                st.text_area("Variation 1", value=outputs[0][0], height=300)
                st.download_button("📥 Download Var 1", data=outputs[0][0], file_name="ManifestAI_Var1.txt", key="dl_1")
            with c2:
                st.info(f"🛡️ Var 2 Validation: {outputs[1][1]}")
                st.text_area("Variation 2 (+ Creativity)", value=outputs[1][0], height=300)
                st.download_button("📥 Download Var 2", data=outputs[1][0], file_name="ManifestAI_Var2.txt", key="dl_2")
        else:
            st.info(f"🛡️ Validation: {outputs[0][1]}")
            st.text_area("Result", value=outputs[0][0], height=300)
            st.download_button("📥 Download Result", data=outputs[0][0], file_name="ManifestAI_Result.txt", key="dl_main")

with tab_hist:
    col_hist_title, col_hist_btn = st.columns([8, 2])
    with col_hist_title:
        st.subheader("📚 Content History & Versions")
    with col_hist_btn:
        # NEW: Clear History Button
        if st.button("🗑️ Clear History"):
            with open(HISTORY_FILE, "w") as f: json.dump([], f)
            st.success("History Cleared!")
            st.rerun()

    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r") as f:
            try:
                hist_data = json.load(f)
                if not hist_data: st.write("History is empty.")
                for item in hist_data:
                    with st.expander(f"{item['timestamp']} | {item['type']}"):
                        st.write("**Topic:**", item['topic'])
                        st.code(item['output'], language="markdown")
            except:
                st.write("History is empty.")
    else:
        st.write("No content generated yet.")