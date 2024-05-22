"""
At the command line, only need to run once to install the package via pip:

$ pip install google-generativeai
"""
import os

import google.generativeai as genai
from dotenv import load_dotenv

from src.ask_llm.local_llm import gpt4all_client

load_dotenv()
# Load genai key from environment variable
GENAI_KEY = os.getenv("GENAI_KEY")
genai.configure(api_key=GENAI_KEY)

# Set up the model
generation_config = {
    "temperature": 0,
    "top_p": 1,
    "top_k": 1,
    "max_output_tokens": 3048,
}

safety_settings = [
    {
        "category": "HARM_CATEGORY_HARASSMENT",
        "threshold": "BLOCK_NONE"
    },
    {
        "category": "HARM_CATEGORY_HATE_SPEECH",
        "threshold": "BLOCK_NONE"
    },
    {
        "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
        "threshold": "BLOCK_NONE"
    },
    {
        "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
        "threshold": "BLOCK_NONE"
    },
]

model = genai.GenerativeModel(
    model_name="gemini-1.0-pro-001",
    generation_config=generation_config,
    safety_settings=safety_settings)


def get_history_flavor(history, question, flavor="gpt4all"):
    copied_history = history.copy()
    if flavor == "gemini":
        for message in copied_history:
            if "content" in message:
                message["parts"] = [message["content"]]
                del message["content"]

        return copied_history

    elif flavor == "gpt4all":
        return history + [
            {
                "role": "user",
                "content": question,
            }]


def ask_llm(history, question, model_name="gemini"):
    history = get_history_flavor(history, question, flavor=model_name)

    if model_name == "gemini":
        convo = model.start_chat(history=history)
        convo.send_message(question)
        return convo.last.text

    elif "gpt4all":
        output = gpt4all_client.chat.completions.create(
            messages=history,
            max_tokens=generation_config["max_output_tokens"],
            temperature=generation_config["temperature"],
            top_p=generation_config["top_p"],
            n=1,
            stream=False,
            model="Nous-Hermes-2-Mistral-7B-DPO.Q4_0.gguf",
        )

        return output.choices[0].message.content
