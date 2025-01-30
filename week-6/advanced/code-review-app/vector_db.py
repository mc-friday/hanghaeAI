from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.schema import Document
from utils import log_message

# 최신 HuggingFace 임베딩 모델 적용
embedding_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

# 벡터 DB 초기화
vectorstore = Chroma(persist_directory="./data", embedding_function=embedding_model)
log_message("✅ 벡터DB 초기화 완료")

def store_review(code, review, improved_code):
    """코드 리뷰 결과를 벡터 DB에 저장"""
    doc = Document(page_content=f"Code:\n{code}\n\nReview:\n{review}\n\nImproved Code:\n{improved_code}")
    vectorstore.add_documents([doc])
    log_message("✅ 리뷰 결과가 벡터DB에 저장됨")

def search_similar_reviews(query):
    """벡터DB에서 유사한 코드 리뷰 검색"""
    results = vectorstore.similarity_search(query, k=3)
    log_message("✅ 벡터DB에서 유사 코드 검색 완료")
    return [doc.page_content for doc in results]