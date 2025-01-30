import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from utils import log_message

# 환경 변수 로드
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")


def detect_language(code):
    """GPT-4o-mini를 사용하여 코드의 프로그래밍 언어 감지"""
    log_message("🔍 프로그래밍 언어 감지 시작")

    model = ChatOpenAI(model_name="gpt-4o-mini", openai_api_key=api_key)

    prompt = f"""
    주어진 코드의 프로그래밍 언어를 감지하세요. 오직 언어명만 출력하세요.
    ```
    {code}
    ```
    """

    response = model.invoke(prompt)  # invoke() 사용
    detected_language = response.content.strip()  # AIMessage에서 문자열 추출

    if not detected_language:
        log_message("❌ 프로그래밍 언어 감지 실패 - 모델 응답이 빈 문자열입니다.")
        raise ValueError("프로그래밍 언어 감지에 실패했습니다.")

    log_message(f"✅ 감지된 언어: {detected_language}")
    return detected_language