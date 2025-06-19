from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
import json
import re
import os

response_prompt = ChatPromptTemplate.from_template("""
You are a friendly and conversational Korean partner helping a Korean learner practice. 

Here is the conversation so far:

{history}

Now, the learner just said:

"{sentence}"

Respond naturally in Korean, continuing the conversation in an engaging way. Follow these rules:

1. **Match the learner's tone**: If the sentence is in 반말 (informal), respond in 반말. If it is in 존댓말 (formal), respond in 존댓말.
2. **Do NOT correct or explain grammar.**
3. **Ask a follow-up question** or comment to keep the conversation going.
4. Keep it simple and friendly. Avoid long or complex sentences.
5. Output must be in the following JSON format:

{{
  "content": "your natural reply in Korean",
  "translation": "your reply translated to English"
}}

Do NOT include any explanation, commentary, or additional text. Only return a valid JSON object.
""")

def get_bot_reply(sentence: str, context: list) -> dict:
    try:
        llm = ChatOpenAI(model="gpt-4", temperature=0.7)

        if not sentence:
            raise ValueError("❗️입력 문장이 비어 있습니다.")

        # context: List[ContextMessage] → 문자열 history로 변환
        history = ""
        for turn in context:
            role = turn.role  # ✅ 속성 접근
            content = turn.content
            prefix = "User" if role == "user" else "Bot"
            history += f"{prefix}: {content}\n"

        messages = response_prompt.format_messages(sentence=sentence, history=history.strip())
        response = llm(messages)

        raw = response.content.strip()

        # 중괄호 블록 추출 (가장 바깥 JSON 객체 찾기)
        match = re.search(r'\{[\s\S]*\}', raw)
        if match:
            parsed = json.loads(match.group())
            print("✅ JSON 파싱 성공!")
            return parsed

        # JSON 블록이 없으면 fallback
        print("⚠️ JSON 패턴 매칭 실패")
        raise json.JSONDecodeError("No valid JSON object found", raw, 0)

    except json.JSONDecodeError:
        print("❗️Chatbot 응답 파싱 실패:\n", raw)
        return {
            "content": "잘 이해했어요!",
            "translation": "Got it!"
        }