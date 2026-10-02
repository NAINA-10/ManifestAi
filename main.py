import os, json, datetime
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_groq import ChatGroq
from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

load_dotenv(override=True)

HISTORY_FILE = "history.json"
PREFS_FILE = "prefs.json"

llm_gemini = ChatGoogleGenerativeAI(model="gemini-2.5-flash", api_key=os.getenv("GOOGLE_API_KEY"))
llm_groq = ChatGroq(model="llama-3.3-70b-versatile", api_key=os.getenv("GROQ_API_KEY"))
llm_ollama = ChatOllama(model="llama3.2:1b")

def get_selection(title, options, default_idx=0, allow_multiple=False):
    print(f"\n🔹 {title} (Default: [{options[default_idx]}]):")
    for i, opt in enumerate(options, 1): print(f"  {i}. {opt}")
    if not allow_multiple: print(f"  {len(options) + 1}. Other (Type Manually)")

    while True:
        prompt_msg = f"  👉 Select numbers (comma-separated) or press ENTER: " if allow_multiple else f"  👉 Select (1-{len(options) + 1}) or press ENTER: "
        choice = input(prompt_msg).strip()

        if not choice: return [options[default_idx]] if allow_multiple else options[default_idx]

        if allow_multiple:
            try:
                indices = [int(x.strip()) - 1 for x in choice.split(',')]
                return [options[i] for i in indices if 0 <= i < len(options)]
            except: print("  ❌ Invalid. Format like: 1,3")
        else:
            if choice.isdigit():
                idx = int(choice) - 1
                if 0 <= idx < len(options): return options[idx]
                elif idx == len(options): return input("  ✍️ Enter Custom Value: ").strip()
            print("  ❌ Invalid selection.")

def analyze_text(text, target_keywords):
    words = text.split()
    pos_score = sum(1 for w in words if w.lower().strip('.,!?') in {'great', 'excellent', 'happy', 'success', 'growth', 'best'})
    neg_score = sum(1 for w in words if w.lower().strip('.,!?') in {'bad', 'terrible', 'fail', 'worst', 'hard', 'issue'})
    sentiment = "Positive 🟢" if pos_score > neg_score else "Negative 🔴" if neg_score > pos_score else "Neutral ⚪"
    kw_found = sum(1 for k in target_keywords.split(',') if k.strip().lower() in text.lower()) if target_keywords and target_keywords.lower() != "none" else 0
    return len(words), sentiment, kw_found

def validate_content(content, content_type, include_hashtags, cta_choice):
    status_msgs = []
    if include_hashtags == "Yes" and "#" not in content: content += "\n\n#Trending #Innovation #ManifestAI"; status_msgs.append("Added Hashtags")
    if cta_choice != "None" and "click" not in content.lower(): content += f"\n\n👉 {cta_choice}"; status_msgs.append("Added CTA")
    if content_type == "Professional Email" and "Subject:" not in content: content = "Subject: Important Update\n\n" + content; status_msgs.append("Added Subject Line")
    return content, "FIXED: " + ", ".join(status_msgs) if status_msgs else "PASSED"

audience_options = ["Corporate Executives / B2B", "Tech-Savvy Millennials", "Gen Z Consumers", "Small Business Owners", "Job Seekers", "Investors & VCs", "Existing Customers", "General Public"]
persona_options = ["Corporate CEO", "Marketing Expert", "Software Engineer", "HR Manager", "Sales Representative", "Industry Thought Leader", "Customer Support"]
goal_options = ["Sales/Conversion", "Lead Generation", "Brand Awareness", "Engagement & Community", "Educational / Value Add", "Thought Leadership", "Event Promotion"]
content_options = ["LinkedIn Post", "Professional Email", "Ad Copy", "Twitter Thread", "Blog Post"]
tone_options = ["Professional", "Engaging", "Persuasive", "Casual", "Urgent", "Empathetic", "Witty", "Authoritative", "Inspirational"]
format_options = ["Plain Text", "Bullet Points", "Markdown", "Numbered List", "Formal Letter", "Script / Dialogue"]
cta_options = ["None", "Share your thoughts in the comments 👇", "Click the link to learn more 🔗", "Hurry up! Limited time offer ⏳", "Book a Demo today 📅", "Reply to this email ✉️", "Subscribe for more updates 🔔"]

user_prefs = {}
if os.path.exists(PREFS_FILE):
    try:
        with open(PREFS_FILE, "r") as f: user_prefs = json.load(f)
    except: pass

if __name__ == "__main__":
    print("===========================================")
    print(" 🚀 MANIFESTAI ENGINE PRO (CLI) ")
    print("===========================================")

    while True:
        # NEW: Provide a 'clear' command to the user
        topic = input("\n📝 Enter Topic (or 'exit' to quit, 'clear' to empty history): ").strip()

        if topic.lower() == 'exit': break
        if topic.lower() == 'clear':
            with open(HISTORY_FILE, "w") as f: json.dump([], f)
            print("🗑️  History successfully cleared!")
            continue

        content_type = get_selection("Content Type", content_options)

        def_aud = 0; def_per = 0; def_goal = 0; def_fmt = 0; def_emj = 0; def_hash = 0; def_cta = 0
        if content_type == "LinkedIn Post": def_aud = 0; def_per = 5; def_goal = 5; def_fmt = 1; def_emj = 0; def_hash = 0; def_cta = 1
        elif content_type == "Professional Email": def_aud = 6; def_per = 4; def_goal = 1; def_fmt = 4; def_emj = 1; def_hash = 1; def_cta = 5
        elif content_type == "Ad Copy": def_aud = 2; def_per = 1; def_goal = 0; def_fmt = 0; def_emj = 0; def_hash = 1; def_cta = 2

        if user_prefs:
            if user_prefs.get('goal') in goal_options: def_goal = goal_options.index(user_prefs['goal'])
            if user_prefs.get('audience') in audience_options: def_aud = audience_options.index(user_prefs['audience'])

        goal = get_selection("Primary Goal", goal_options, default_idx=def_goal)
        brand_name = input(f"🏢 Brand Name (Press Enter to use '{user_prefs.get('brand', 'Generic')}'): ").strip() or user_prefs.get('brand', 'Generic')
        target_audience = get_selection("Target Audience", audience_options, default_idx=def_aud)
        persona = get_selection("Author Persona", persona_options, default_idx=def_per)
        expertise = get_selection("Audience Expertise", ["Beginner", "Intermediate", "Expert"], default_idx=1)

        tones_list = get_selection("Tones (Select Multiple using commas, e.g., 1,3)", tone_options, default_idx=0, allow_multiple=True)
        tones_str = ", ".join(tones_list)

        output_format = get_selection("Output Format", format_options, default_idx=def_fmt)
        length = get_selection("Length", ["Short", "Medium (Paragraph)", "Long"], default_idx=1)
        emojis = get_selection("Include Emojis?", ["Yes", "No"], default_idx=def_emj)
        hashtags = get_selection("Include Hashtags?", ["Yes", "No"], default_idx=def_hash)
        cta = get_selection("Call to Action (CTA)", cta_options, default_idx=def_cta)
        keywords = input("🔑 Keywords to include (or press Enter): ").strip() or "None"
        words_to_avoid = input("🚫 Words to Avoid (or press Enter): ").strip() or "None"

        compare_mode = get_selection("Generate 2 Variations (Compare Mode)?", ["No", "Yes"], default_idx=0) == "Yes"

        print(f"\n🚀 Manifesting...")

        template = """BRAND NAME: {brand_name} | GOAL: {goal}
        TARGET AUDIENCE: {target_audience} (Level: {expertise}) | AUTHOR PERSONA: {persona}
        CONTENT TYPE: {content_type} | COMBINED TONES: {tone} | LENGTH: {length} | OUTPUT FORMAT: {output_format}
        KEYWORDS: {keywords} | WORDS TO AVOID: {words_to_avoid}
        FORMATTING RULES: Emojis: {emojis}, Hashtags: {hashtags}, Required CTA: {cta}
        TOPIC: {topic}
        INSTRUCTIONS: Generate the {content_type}. Blend the requested TONES. Strictly use {output_format}. If Emojis 'No', use ZERO emojis."""
        prompt = ChatPromptTemplate.from_template(template)
        chain_inputs = {"topic": topic, "brand_name": brand_name, "goal": goal, "target_audience": target_audience, "persona": persona, "expertise": expertise, "content_type": content_type, "tone": tones_str, "length": length, "output_format": output_format, "keywords": keywords, "words_to_avoid": words_to_avoid, "emojis": emojis, "hashtags": hashtags, "cta": cta}

        variations = 2 if compare_mode else 1
        outputs = []
        used_engine = "ManifestAI Core ✨"

        for i in range(variations):
            current_temp = 0.7 if i == 0 else 0.9
            try: llm_gemini.temperature = current_temp; raw = (prompt | llm_gemini | StrOutputParser()).invoke(chain_inputs)
            except:
                try: llm_groq.temperature = current_temp; raw = (prompt | llm_groq | StrOutputParser()).invoke(chain_inputs)
                except: llm_ollama.temperature = current_temp; raw = (prompt | llm_ollama | StrOutputParser()).invoke(chain_inputs)

            final_output, val_status = validate_content(raw, content_type, hashtags, cta)
            outputs.append((final_output, val_status))

        words, sentiment, kw_found = analyze_text(outputs[0][0], keywords)

        print("\n" + "="*60)
        print(f"✨ MANIFESTATION COMPLETE | ENGINE: {used_engine} | 📊 WORDS: {words} | 🎭 SENTIMENT: {sentiment} | 🔑 KWs: {kw_found}")
        print("="*60)

        print(f"\n[ VARIATION 1 | {outputs[0][1]} ]\n{outputs[0][0]}\n")
        if compare_mode:
            print(f"\n[ VARIATION 2 (+Creativity) | {outputs[1][1]} ]\n{outputs[1][0]}\n")

        if input("💾 Save to Version History? (y/n): ").strip().lower() == 'y':
            hist = []
            if os.path.exists(HISTORY_FILE):
                with open(HISTORY_FILE, "r") as f:
                    try: hist = json.load(f)
                    except: pass
            hist.insert(0, {"timestamp": str(datetime.datetime.now())[:16], "topic": topic[:50], "type": content_type, "engine": used_engine, "output": outputs[0][0]})
            with open(HISTORY_FILE, "w") as f: json.dump(hist[:50], f)
            print("✅ Saved to History.")

        if input("📥 Download output to .txt file? (y/n): ").strip().lower() == 'y':
            with open("ManifestAI_Output.txt", "w") as f:
                f.write(outputs[0][0])
                if compare_mode: f.write("\n\n--- VARIATION 2 ---\n\n" + outputs[1][0])
            print("✅ Saved to ManifestAI_Output.txt")