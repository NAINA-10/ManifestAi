import os
import sys
# Ensures the script can find the .env file in the parent directory
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from dotenv import load_dotenv

# Initialize environment variables (API Keys)
load_dotenv()

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

# 1. SETUP MODEL
# Using 'gemini-2.5-flash' for high-speed performance and a large 1M context window.
llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.7)

# 2. SETUP PROMPT
# Define a dynamic template that accepts 'role' and 'topic' for persona-based generation.
template = """
You are an expert AI Assistant.
ROLE: {role}
TOPIC: {topic}

Write a short response strictly in the requested role.
"""
prompt = ChatPromptTemplate.from_template(template)

# Chain: Links the prompt, LLM, and string output parser for a clean text response.
chain = prompt | llm | StrOutputParser()

# 3. INTERACTIVE TESTING LOOP
print("--- TESTING: GOOGLE GEMINI ---")
while True:
    topic = input("\nEnter Topic (or 'exit'): ")
    if topic.lower() == 'exit': break

    role = input("Enter Role (e.g., Expert, Comedian): ")

    print(f"\nGenerating via Gemini...")
    # Invoke the chain with user inputs
    response = chain.invoke({"role": role, "topic": topic})
    print(f"\nRESULT:\n{response}\n" + "-"*30)