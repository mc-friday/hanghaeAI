from vector_db import search_similar_reviews
from utils import log_message


def retrieve_similar_code(query):
    """입력 코드와 유사한 코드 검색 (RAG)"""
    log_message("🔍 유사 코드 검색 시작")
    results = search_similar_reviews(query)

    if not results:
        log_message("⚠️ 유사 코드 검색 결과가 없음 - 기본 코드 리뷰 예시 제공")
        return "유사한 코드가 없습니다. 하지만 다음은 일반적인 코드 개선 예시입니다:\n\n1. 주석을 추가하세요.\n2. 예외 처리를 강화하세요.\n3. 코드 중복을 줄이세요."

    log_message("✅ 유사 코드 검색 완료")

    log_message("⚠️ 유사 코드 검색 결과가 없음 - 기본 코드 리뷰 예시 제공")
    return "유사한 코드가 없습니다. 하지만 다음은 일반적인 코드 개선 예시입니다:\n\n1. 주석을 추가하세요.\n2. 예외 처리를 강화하세요.\n3. 코드 중복을 줄이세요."

    # return "\n\n".join(results)