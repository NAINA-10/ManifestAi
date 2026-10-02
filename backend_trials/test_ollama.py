import os
# Modern LangChain-Ollama integration (prevents Deprecation Warnings)
from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

# 1. SETUP MODEL
# Using 'llama3.2:1b' - a lightweight model optimized for laptops with limited RAM.
# Ensure Ollama is running in the background before execution.
llm = ChatOllama(
    model="llama3.2:1b",
    temperature=0.7
)

# 2. SETUP PROMPT
template = """
You are an expert AI Assistant.
ROLE: {role}
TOPIC: {topic}

Write a short response strictly in the requested role.
"""
prompt = ChatPromptTemplate.from_template(template)
chain = prompt | llm | StrOutputParser()

# 3. LOCAL EXECUTION LOOP
print("--- TESTING: OLLAMA (LOCAL LLAMA 3.2 1B) ---")
while True:
    topic = input("\nEnter Topic (or 'exit'): ")
    if topic.lower() == 'exit': break

    role = input("Enter Role (e.g., Expert, Student): ")

    print(f"\nGenerating locally via Ollama...")
    try:
        # This talks to the local server (usually http://localhost:11434)
        response = chain.invoke({"role": role, "topic": topic})
        print(f"\nRESULT:\n{response}\n" + "-"*30)
    except Exception as e:
        print(f"❌ Error: {e}")