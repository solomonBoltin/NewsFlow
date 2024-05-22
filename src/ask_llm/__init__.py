from src.ask_llm.models.gemini import gemini_model, generation_config
from src.ask_llm.models.gpt4all import gpt4all_client, gpt4all_generation_config


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
        convo = gemini_model.start_chat(history=history)
        convo.send_message(question)
        return convo.last.text

    elif "gpt4all":
        output = gpt4all_client.chat.completions.create(
            messages=history,
            **gpt4all_generation_config
        )

        return output.choices[0].message.content
