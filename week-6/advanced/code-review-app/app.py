import streamlit as st
import time
from review_model import review_code
from language_detector import detect_language
from vector_db import store_review
from utils import log_message

# ✅ 세션 상태 초기화
if "review_running" not in st.session_state:
    st.session_state["review_running"] = False
if "review_result" not in st.session_state:
    st.session_state["review_result"] = None
if "error_message" not in st.session_state:
    st.session_state["error_message"] = None

st.title("🔍 [6주차]심화과제")

user_code = st.text_area("💻 리뷰할 함수 코드를 입력하세요", height=550)

# ✅ UI 요소를 위한 공간 확보
button_placeholder = st.empty()
status_placeholder = st.empty()
review_result_placeholder = st.empty()


# 🚀 코드 리뷰 실행 함수 (동기 실행)
def run_review():
    try:
        start_time = time.time()
        log_message("🚀 run_review() 실행 시작")

        # ✅ 상태 업데이트
        st.session_state["review_running"] = True
        st.session_state["error_message"] = None
        st.session_state["review_result"] = None  # 이전 결과 초기화

        status_placeholder.empty()  # 이전 메시지 제거
        status_message = status_placeholder.status("🔍 코드 분석 중...", expanded=True)  # ✅ 상태 메시지 업데이트

        time.sleep(1)  # UI 업데이트를 위한 대기

        # 🚀 언어 감지
        detect_start = time.time()
        log_message("🚀 detect_language() 실행 시작")
        language = detect_language(user_code)
        detect_time = time.time() - detect_start
        log_message(f"✅ detect_language() 완료 - 감지된 언어: {language} (소요 시간: {detect_time:.2f}초)")

        # 🚀 코드 리뷰 실행
        review_start = time.time()
        log_message("🚀 review_code() 실행 시작")
        review_result, improved_code, score, additional_feedback = review_code(user_code, language)
        review_time = time.time() - review_start
        log_message(f"✅ review_code() 완료 - 점수: {score} (소요 시간: {review_time:.2f}초)")

        # 🚀 벡터DB 저장
        store_start = time.time()
        log_message("🚀 store_review() 실행 시작")
        store_review(user_code, review_result, improved_code)
        store_time = time.time() - store_start
        log_message(f"✅ store_review() 완료 (소요 시간: {store_time:.2f}초)")

        # ✅ 결과 저장
        st.session_state["review_result"] = {
            "language": language,
            "score": score,
            "review_result": review_result,
            "improved_code": improved_code,
            "additional_feedback": additional_feedback
        }

        # ✅ 리뷰 완료 후 상태 업데이트
        st.session_state["review_running"] = False

        # ✅ "🔍 코드 분석 중..." 메시지 제거
        status_placeholder.empty()

        log_message(f"✅ run_review() 완료 (총 소요 시간: {time.time() - start_time:.2f}초)")

    except Exception as e:
        log_message(f"❌ run_review() 실행 중 오류 발생: {str(e)}")
        st.session_state["error_message"] = str(e)
        st.session_state["review_running"] = False
        status_placeholder.empty()  # 오류 발생 시 상태 메시지 제거


# ✅ 버튼 렌더링
with button_placeholder:
    if st.button("🚀 코드 리뷰 시작", key="start_button"):
        log_message("✅ 코드 리뷰 시작 버튼 클릭됨")
        run_review()  # 🚀 동기 실행

# ✅ 리뷰 결과 표시
if st.session_state["review_result"]:
    review_data = st.session_state["review_result"]

    with review_result_placeholder.container():
        st.subheader("📌 코드 리뷰 결과")
        st.write(f"🔹 **감지된 언어:** {review_data['language']}")
        st.write(f"📊 **코드 품질 점수:** {review_data['score']}/100")

        st.subheader("📢 리뷰 피드백")
        st.markdown(review_data["review_result"], unsafe_allow_html=True)

        if isinstance(review_data["additional_feedback"], list) and review_data["additional_feedback"]:
            st.subheader("💡 추가 피드백")
            feedback_summary = "\n".join(
                [f"🔹 **{item.get('issue', '기타 피드백')}** - {item.get('suggestion', '내용 없음')}" for item in
                 review_data["additional_feedback"]]
            )
            st.markdown(feedback_summary, unsafe_allow_html=True)

        st.subheader("🚀 개선된 코드")
        st.code(review_data["improved_code"], language=review_data["language"].lower())

# 🚨 오류 메시지 표시
if st.session_state["error_message"]:
    st.error(f"🚨 오류 발생: {st.session_state['error_message']}")