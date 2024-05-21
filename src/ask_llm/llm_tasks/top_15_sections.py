import json

from openai import APIConnectionError

from src.ask_llm.__init__ import ask_llm


def ask_ai_on_top_15_sections(base_url, input_urls, model_name="gpt4all", max_retries=3):
    """
    Selects the top 15 sections most likely to contain stock market relevant articles using an AI model.

    Args:
        base_url (str): The base URL of the news website.
        input_urls (list): A list of URLs to analyze.
        model_name (str, optional): The name of the AI model to use. Defaults to "gpt4all".
        max_retries (int, optional): Maximum number of retries for API calls. Defaults to 3.

    Returns:
        list: A list of the 15 selected URLs.
    """

    prompt = """You will be given a list of URLs from a news website. Your task is to analyze these URLs and identify the 15 sections that are most likely to contain articles with the potential to significantly impact the stock market.

Consider prioritizing sections related to:

* **Economic News:** Look for sections covering macroeconomic indicators (GDP, unemployment, inflation), central bank policies (interest rates, quantitative easing), and government policies & regulations (taxation, trade).
* **Company-Specific News:** Focus on sections featuring earnings reports, mergers & acquisitions, product launches & innovations, and management changes within major companies or key industries.
* **Industry & Sector News:** Prioritize sections related to technological advancements, industry regulations, and supply chain developments within influential sectors.
* **Geopolitical Events:** Include sections covering political instability, international conflicts, trade agreements, and major geopolitical events with potential global economic impact.
* **Global Events:** Consider sections discussing pandemics, natural disasters, climate change, and other significant events with the potential to disrupt economic activity or influence investor sentiment.

Your output should be a list of the 15 selected section URLs in json format.  {"sections":[]}"""

    for retries in range(max_retries):
        try:
            full_prompt = f"base_url={base_url}\ninput_urls={input_urls}\n\n{prompt}"
            response_text = ask_llm(
                [],  # No history needed for this task
                full_prompt,
                model_name=model_name
            )
            json_string = response_text[response_text.find("{"):response_text.rfind("}") + 1]
            json_response = json.loads(json_string)
            selected_urls = json_response.get("sections", [])

            if len(selected_urls) > 2:
                return selected_urls[:15]
            else:
                print(f"AI model returned {len(selected_urls)} URLs instead of 15. Retrying...")
        except (json.JSONDecodeError, ValueError) as e:
            print(f"Error parsing JSON (attempt {retries + 1}): ", e)
            print("Response: ", response_text)
        except (ConnectionError, APIConnectionError) as e:
            print(f"Connection error (attempt {retries + 1}): ", e)

    print("Failed to get valid response from AI model after multiple retries.")
    raise ValueError("Failed to get valid response from AI model after multiple retries.")


