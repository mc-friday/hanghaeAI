import os
import base64
import streamlit as st
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage

# .env 파일 로드
load_dotenv()

# 환경 변수에서 OpenAI API 키 가져오기
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# OpenAI 모델 설정
model = ChatOpenAI(model="gpt-4o", openai_api_key=OPENAI_API_KEY)


def encode_image(image_file):
    """이미지를 Base64로 인코딩하는 함수"""
    return base64.b64encode(image_file.read()).decode("utf-8")


# Streamlit UI 설정
st.title("[6주차]기본과제")

# 여러 장의 이미지 업로드 기능
uploaded_images = st.file_uploader(
    "여러 장의 이미지를 업로드하세요!", type=["png", "jpg", "jpeg"], accept_multiple_files=True
)

# 세션 상태에서 이미지 데이터를 유지
if "image_data_list" not in st.session_state:
    st.session_state.image_data_list = []
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "waiting_for_response" not in st.session_state:
    st.session_state.waiting_for_response = False

# 업로드된 이미지 표시 및 Base64 인코딩
image_data_list = []
if uploaded_images:
    for img in uploaded_images:
        st.image(img, caption=img.name, use_container_width=True)
        image_data_list.append({
            "type": "image_url",
            "image_url": {"url": f"data:image/jpeg;base64,{encode_image(img)}"}
        })
    # 이미지 데이터를 세션 상태에 저장하여 유지
    st.session_state.image_data_list = image_data_list

# 이전 대화 출력
for chat in st.session_state.chat_history:
    with st.chat_message(chat["role"]):
        st.markdown(chat["content"])

# 사용자 질문 입력 받기
if not st.session_state.waiting_for_response:
    user_question = st.text_input("이미지에 대해 질문해보세요!", key="user_input")

    if user_question:
        with st.chat_message("user"):
            st.markdown(user_question)

        # 챗봇이 생각 중임을 표시
        with st.chat_message("assistant"):
            st.markdown("생각중입니다...")

        # 대화 히스토리에 추가
        st.session_state.chat_history.append({"role": "user", "content": user_question})
        st.session_state.waiting_for_response = True
        st.session_state.last_question = user_question
        st.rerun()

# 답변 생성 로직
if st.session_state.waiting_for_response and "last_question" in st.session_state:
    user_question = st.session_state.last_question
    message = HumanMessage(
        content=[
            {"type": "text", "text": user_question},
            *st.session_state.image_data_list  # 업로드된 모든 이미지 포함
        ],
    )
    result = model.invoke([message])  # 모델 호출
    response = result.content  # 응답 내용 가져오기

    with st.chat_message("assistant"):
        st.markdown(response)

    # 대화 히스토리에 추가
    st.session_state.chat_history.append({"role": "assistant", "content": response})
    st.session_state.waiting_for_response = False
    del st.session_state.last_question

    # 새로운 입력을 받을 수 있도록 포커스 설정
    st.experimental_set_query_params(focus="user_input")
    st.rerun()