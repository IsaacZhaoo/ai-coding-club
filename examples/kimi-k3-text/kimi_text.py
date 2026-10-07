import os

from openai import OpenAI

with OpenAI(
    api_key=os.environ["MOONSHOT_API_KEY"],
    base_url=os.environ["MOONSHOT_BASE_URL"],
) as client:
    completion = client.chat.completions.create(
        model="kimi-k3",
        reasoning_effort="low",
        max_completion_tokens=4096,
        messages=[
            {"role": "user", "content": "Describe a code review in one sentence."}
        ],
    )

choice = completion.choices[0]
if choice.finish_reason != "stop" or not choice.message.content:
    raise RuntimeError(f"No complete text answer: finish_reason={choice.finish_reason}")

print(choice.message.content)
