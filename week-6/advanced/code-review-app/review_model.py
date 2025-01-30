import os
import json
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from retriever import retrieve_similar_code
from agent import CodeReviewAgent
from utils import log_message

# 환경 변수 로드
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")


def review_code(code, language):
    """GPT-4o-mini + RAG + Agent 기반 코드 리뷰 및 개선"""
    log_message(f"코드 리뷰 시작 - 감지된 언어: {language}")

    model = ChatOpenAI(model_name="gpt-4o-mini", openai_api_key=api_key)

    # 유사 코드 검색 (RAG)
    similar_code = retrieve_similar_code(code)
    log_message("유사 코드 검색 완료")

    # 🚀 프롬프트 수정: "응답을 반드시 한글로 제공하세요"
    prompt_review = f"""
    {language} 코드입니다. 코드 리뷰를 진행해 주세요.

    1. 코드의 문제점을 설명하세요.
    2. 코드 품질 점수를 1~100 사이로 평가하세요.
    3. 개선된 코드를 제시하세요.
    4. **추가 피드백을 제공하세요.** (⚠️ **추가 피드백에는 코드 포함 금지** ⚠️)

    참고할 유사 코드:
    ```
    {similar_code}
    ```

    **❗ 중요한 요구사항 ❗**
    - **응답을 반드시 한글로 작성하세요.**
    - **JSON 형식으로 반환해야 합니다.**
    - **추가 피드백(`additional_feedback`)에는 코드가 포함되지 않아야 합니다.**

    ```json
    {{
        "review": [
            {{"issue": "보안 문제", "description": "비밀 키가 노출됨", "suggestion": "보안 저장소를 사용하세요."}},
            {{"issue": "코드 중복", "description": "암호화 로직이 중복됨", "suggestion": "공통 로직을 리팩토링하세요."}}
        ],
        "score": 85,
        "improved_code": "...",
        "additional_feedback": [
            {{"issue": "보안 개선", "suggestion": "비밀 키 및 IV를 환경 변수로 관리하세요."}},
            {{"issue": "리팩토링 필요", "suggestion": "중복된 로직을 제거하여 유지보수성을 향상시키세요."}}
        ]
    }}
    ```
    """

    # 모델 응답 요청
    response = model.invoke(prompt_review)
    response_clean = response.content.strip()

    log_message(f"모델 응답 수신 완료: {response_clean[:500]}")  # 긴 응답일 경우 앞부분만 로깅

    # 불필요한 "```json" 태그 제거 후 JSON 변환
    response_clean = response_clean.replace("```json", "").replace("```", "").strip()

    try:
        review_data = json.loads(response_clean)
        log_message(f"✅ JSON 변환 성공 - 응답 데이터: {review_data}")
    except json.JSONDecodeError as e:
        log_message(f"❌ JSON 변환 오류: {e} - 응답 내용: {response_clean}")
        raise ValueError("모델 응답이 유효한 JSON 형식이 아닙니다.")

    score = review_data.get("score", 50)
    log_message(f"✅ 리뷰 완료 - 점수: {score}")

    # ✅ JSON 내 "review" 항목을 한글로 변환된 상태에서 정리
    review_text = review_data.get("review", [])
    formatted_review = []

    if isinstance(review_text, list):
        for item in review_text:
            if isinstance(item, dict):
                formatted_review.append(
                    f"🔹 **{item.get('issue', '문제 없음')}**\n   - {item.get('description', '')}\n   - **💡 개선 방법:** {item.get('suggestion', '')}")
            else:
                formatted_review.append(str(item))  # dict가 아닌 경우에도 안전하게 변환
        review_text = "\n\n".join(formatted_review)

    else:
        review_text = str(review_text)

    # ✅ 추가 피드백 가공
    additional_feedback = review_data.get("additional_feedback", [])
    formatted_feedback = []

    if isinstance(additional_feedback, list):
        for item in additional_feedback:
            if isinstance(item, dict):
                formatted_feedback.append(
                    f"⚡ **{item.get('issue', '기타 피드백')}**\n   - {item.get('suggestion', '추가 피드백이 제공되지 않았습니다.')}")
            else:
                formatted_feedback.append(str(item))  # dict가 아닌 경우 안전하게 변환
        formatted_feedback = "\n\n".join(formatted_feedback)
    else:
        formatted_feedback = "추가 피드백이 제공되지 않았습니다."

    # ✅ UI에서 올바르게 표시되도록 보완
    final_review = f"""
## 📊 코드 품질 점수: {score}/100

### 📢 리뷰 피드백
{review_text}

---

### 💡 추가 피드백
{formatted_feedback}
"""

    log_message("✅ UI 렌더링 최적화 완료")

    return final_review, review_data.get("improved_code", "N/A"), score, formatted_feedback