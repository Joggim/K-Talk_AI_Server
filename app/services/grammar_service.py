from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
import json
import re

# LangChain Prompt Template
grammar_prompt = ChatPromptTemplate.from_template("""
You are a Korean language teacher. A Korean learner said:
"{sentence}"

Evaluate the grammar and expression quality of this Korean sentence.
If there are any mistakes, respond with a correction and a brief explanation.
If the sentence is already correct, say so clearly.

Respond only in this JSON format:

{{
  "isFeedback": true or false,  // true if correction is needed
  "suggestion": "corrected sentence in Korean (or same sentence if no errors)",
  "explanation": "brief explanation in English (or empty if no correction needed)"
}}

Do not include any commentary or extra text outside the JSON object.
""")

# Grammar Feedback 실행 함수
async def get_grammar_feedback(sentence: str) -> dict:
    try:
        llm = ChatOpenAI(model="gpt-4", temperature=0)

        if not sentence:
            raise ValueError("❗️입력 문장이 비어 있습니다.")

        messages = grammar_prompt.format_messages(sentence=sentence)

        response = await llm.ainvoke(messages)

        raw = response.content.strip()

        # 중괄호 블록 추출
        match = re.search(r'\{[\s\S]*\}', raw)
        if match:
            parsed = json.loads(match.group())
            return parsed

        raise json.JSONDecodeError("No valid JSON object found", raw, 0)

    except json.JSONDecodeError:
        print("❗️Grammar 응답 파싱 실패:\n", raw)
        return {
            "suggestion": sentence,
            "explanation": "Failed to parse response. Please try again."
        }
    except Exception as e:
        print("❗️Grammar Feedback 예외 발생:", e)
        return {
            "suggestion": sentence,
            "explanation": str(e)
        }