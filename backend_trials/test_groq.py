import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from dotenv import load_dotenv

load_dotenv()

from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

# Security check for the API key
if not os.getenv("GROQ_API_KEY"):
    print("❌ Error: GROQ_API_KEY missing in .env")
    exit()

# 1. SETUP MODEL
# Using 'llama-3.3-70b-versatile', currently the most powerful stable model on Groq.
llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0.7)

# 2. SETUP PROMPT (Architecture remains consistent across modules for modularity)
template = """
You are an expert AI Assistant.
ROLE: {role}
TOPIC: {topic}

Write a short response strictly in the requested role.
"""
prompt = ChatPromptTemplate.from_template(template)
chain = prompt | llm | StrOutputParser()

# 3. INTERACTIVE TESTING LOOP
print("--- TESTING: GROQ (LLAMA 3.3) ---")
while True:
    topic = input("\nEnter Topic (or 'exit'): ")
    if topic.lower() == 'exit': break

    role = input("Enter Role (e.g., Expert, Comedian): ")

    print(f"\nGenerating via Groq...")
    response = chain.invoke({"role": role, "topic": topic})
    print(f"\nRESULT:\n{response}\n" + "-"*30)