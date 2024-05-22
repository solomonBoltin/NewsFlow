from openai import OpenAI
import datetime
import json

# model = "all-MiniLM-L6-v2-f16.gguf"
# model = "replit-code-v1_5-3b-newbpe-q4_0.gguf"
# model = "orca-mini-3b-gguf2-q4_0.gguf"
# model = "gpt4all-falcon-newbpe-q4_0.gguf"
# model = "Nous-Hermes-2-Mistral-7B-DPO.Q4_0.gguf"


api_base = 'http://localhost:4891/v1'

gpt4all_generation_config = {
    "max_tokens": 3048,
    "temperature": 0,
    "top_p": 1,
    "n": 1,
    "stream": False,
    "model": "Nous-Hermes-2-Mistral-7B-DPO.Q4_0.gguf",
}

gpt4all_client = OpenAI(
    # This is the default and can be omitted
    base_url=api_base,
    api_key="not needed for a local LLM",
)


def llm_data_request(prompt):
    response = gpt4all_client.chat.completions.create(
        messages=[
            # {
            #     "role": "system",
            #     "content": request,
            # },
            {
                "role": "user",
                "content": prompt,
            }
        ],
        max_tokens=300,
        temperature=0.1,
        top_p=1,
        n=1,
        stream=False,
        model="Nous-Hermes-2-Mistral-7B-DPO.Q4_0.gguf",
    )

    return response


def get_article_preview_json(html: str):
    html_article_preview_to_json = ("You are given an HTML snippet representing article preview in a news feed."
                                    "Your task is to find and extract three details from it the title, link, date."
                                    "Please provide your response in JSON format (title:str, link:str, date:str). "
                                    "HTML snippet:")

    prompt = html_article_preview_to_json + html

    llm_res = llm_data_request(prompt)
    llm_res_text = llm_res.choices[0].message.content
    print(llm_res_text)

    return json.loads(llm_res_text)


def test_get_article_preview_json():
    time = datetime.datetime.now()

    print(time)

    html = """<div class="cardlist"><div class="image-card"><div class="image-title"><h4><a
    class="smallcard-title" href="https://www.business-standard.com/economy/news/delhi-electricity-demand-to-cross-8gw
    -this-summer-discoms-brace-up-124040800875_1.html">Delhi electricity demand to cross 8GW this summer, discoms brace
    up</a></h4></div><div class="shortvideoimg" style="position:relative"><a class="img-smllnews"
    href="https://www.business-standard.com/economy/news/delhi-electricity-demand-to-cross-8gw-this-summer-discoms-brace
    -up-124040800875_1.html"></a></div></div><div class="MetaPost_metapost__dt07I metapoststyle"><div
    class="MetaPost_metainfo__MmNP0">3 min read <!-- --> Last Updated : <!-- -->Apr 08 2024 | 7:05 PM<!-- -->
    IST</div><div class="MetaPost_metaactions__myUB4"></div></div></div>"""

    res = get_article_preview_json(html)

    print(res)
    assert res["title"] == "Delhi electricity demand to cross 8GW this summer, discoms brace up"
    assert res[
               "link"] == "https://www.business-standard.com/economy/news/delhi-electricity-demand-to-cross-8gw-this-summer-discoms-brace-up-124040800875_1.html"
    assert res["date"] == "Apr 08 2024 | 7:05 PM"

    print(f"Task took: {datetime.datetime.now() - time}")

# while True:
#     try:
#         test_get_article_preview_json()
#         print("Sucsess")
#     except Exception as e:
#         print(f"Exception {e.with_traceback()}")
