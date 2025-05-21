from openai import OpenAI
import os
from dotenv import load_dotenv
import json

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def generate_recommendation_sentences(tag: str, n: int = 50) -> list[dict]:
    prompt = (
        f"""
        You are a helpful assistant for Korean learners who are practicing pronunciation.

Your task is to generate exactly {n} complete Korean sentences to help the learner practice the pronunciation pattern: '{tag}'.

The pronunciation pattern '{tag}' refers to a specific phonological rule in Korean speech. Only generate sentences that include a word where this rule actually applies in real speech — not just words that contain the target sound.

For example:
- If '{tag}' is '된소리되기 ㄲ', include words like '국밥', '학교', where the plain sound becomes tense due to the phonological context.
- Avoid names or proper nouns like '김 씨' or words where the tense sound is native (e.g., '깨끗하다') and not a result of the target rule.

Follow these rules carefully:

1. Each output must be a natural, complete Korean sentence — not just a word or phrase.
2. Each sentence must include a word that clearly demonstrates the pronunciation pattern: '{tag}' in actual phonological context.
3. The sentences must be common and natural in daily Korean conversation (casual or polite).
4. Each sentence must be between 10 and 20 Korean characters long.
5. Do not generate similar or repetitive expressions. Each sentence should be unique.
6. Do not number or format the sentences in any way.
7. For each sentence, provide a clear and simple English translation.
8. Format your response as a valid JSON array of this structure:

[
  {{
    "content": "한국어 문장",
    "translation": "English translation"
  }},
  …
]

Only return the JSON array. Do not include any explanations, commentary, or extra formatting.
"""
    )

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.8,
        max_tokens=3000,
    )

    raw = response.choices[0].message.content

    try:
        results = json.loads(raw)
        if not isinstance(results, list):
            raise ValueError("Expected a list of sentence objects.")
        return results
    except json.JSONDecodeError as e:
        print("❗ JSON 파싱 실패:", e)
        print("GPT 응답 내용:\n", raw)
        return []
