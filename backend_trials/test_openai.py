import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from dotenv import load_dotenv

load_dotenv()

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

if not os.getenv("OPENAI_API_KEY"):
    print("❌ Error: OPENAI_API_KEY missing in .env")
    exit()

# 1. SETUP MODEL
# Using 'gpt-4o-mini', which is faster and more cost-effective than GPT-4 while retaining high intelligence.
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)

# 2. SETUP PROMPT
template = """
You are an expert AI Assistant.
ROLE: {role}
TOPIC: {topic}

Write a short response strictly in the requested role.
"""
prompt = ChatPromptTemplate.from_template(template)
chain = prompt | llm | StrOutputParser()

# 3. INTERACTIVE TESTING LOOP
print("--- TESTING: OPENAI (CHATGPT) ---")
while True:
    topic = input("\nEnter Topic (or 'exit'): ")
    if topic.lower() == 'exit': break

    role = input("Enter Role (e.g., Expert, Comedian): ")

    print(f"\nGenerating via ChatGPT...")
    response = chain.invoke({"role": role, "topic": topic})
    print(f"\nRESULT:\n{response}\n" + "-"*30)