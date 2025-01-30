import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain.tools import Tool
from langchain.prompts import ChatPromptTemplate
from retriever import retrieve_similar_code
from utils import log_message
import re

# 환경 변수 로드
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

class CodeReviewAgent:
    def __init__(self):
        """LangChain AgentExecutor 기반 코드 리뷰 에이전트"""
        log_message("✅ LangChain Agent 초기화")

        # ✅ 최신 LangChain 방식 적용: `llm` 사용
        llm = ChatOpenAI(model_name="gpt-4o-mini", openai_api_key=api_key)

        tools = [
            Tool(name="Retrieve_Code", func=retrieve_similar_code, description="유사 코드 검색"),
        ]

        # ✅ `prompt`를 LangChain `ChatPromptTemplate`으로 변경
        prompt_template = ChatPromptTemplate.from_template(
            "You are an AI code review assistant. Analyze the given code and provide feedback.\n"
            "Use the tools available to you.\n"
            "Previous actions and thoughts:\n"
            "{agent_scratchpad}"
        )

        # ✅ 함수 이름 검증 추가
        for tool in tools:
            if not re.match(r"^[a-zA-Z0-9_-]+$", tool.name):
                log_message(f"❌ 잘못된 함수 이름 감지: {tool.name} -> 올바른 값으로 변경")
                tool.name = re.sub(r"[^a-zA-Z0-9_-]", "_", tool.name)  # 허용된 문자 외에 모두 `_`로 변환

        self.agent = AgentExecutor(
            agent=create_openai_functions_agent(
                llm=llm,
                tools=tools,
                prompt=prompt_template
            ),
            tools=tools,
            handle_parsing_errors=True,  # 응답 오류 시 자동으로 재시도
        )

    def analyze_code(self, code):
        """Agent를 활용하여 추가적인 코드 분석"""
        log_message("🔍 Agent를 활용한 추가 코드 분석 시작")

        try:
            response = self.agent.invoke({"input": f"코드 리뷰를 보완해주세요:\n{code}"})
            log_message("✅ Agent 응답 수신 완료")
            return response
        except Exception as e:
            log_message(f"❌ Agent 오류 발생: {e}")
            return "에이전트 응답을 처리하는 중 오류가 발생했습니다. 다시 시도해주세요."