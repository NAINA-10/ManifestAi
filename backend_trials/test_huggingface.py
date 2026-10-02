import os
from dotenv import load_dotenv
from huggingface_hub import InferenceClient

# Load API credentials from .env
load_dotenv()
token = os.getenv("HUGGINGFACEHUB_API_TOKEN")

if not token:
    print("❌ Missing HF Token")
    exit()

# Initialize the Hugging Face Inference Client
client = InferenceClient(token=token)

print("\n--- HF CHAT MODE ---")

while True:
    topic = input("\nEnter Topic (or exit): ")
    if topic.lower() == "exit":
        break

    role = input("Enter Role (Student / Expert / Kid etc): ")

    # Combine role and topic into a single user instruction
    user_prompt = f"Role: {role}. Topic: {topic}. Explain simply."

    try:
        # Using chat_completion to handle 'conversational' models like Zephyr
        response = client.chat_completion(
            model="HuggingFaceH4/zephyr-7b-beta",
            messages=[
                {"role": "user", "content": user_prompt}
            ]
        )

        print("\nRESULT:")
        # Accessing the specific message content from the API response object
        print(response.choices[0].message.content)

    except Exception as e:
        print("❌ Error:", e)