import os
from langchain_google_genai import ChatGoogleGenerativeAI

# API 키 설정
os.environ['GOOGLE_API_KEY'] = "AIzaSyAOH44lJ4T6qhqSQ8CslLdVP9y2lkyt5ac"

print("API 키 설정됨:", os.getenv('GOOGLE_API_KEY')[:20] + "...")

try:
    # AI 모델 초기화 테스트
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.0-flash-exp",
        temperature=0.1,
        google_api_key=os.getenv('GOOGLE_API_KEY')
    )
    print("✅ AI 모델 초기화 성공!")
    
    # 간단한 테스트 요청
    response = llm.invoke("안녕하세요! 간단한 테스트입니다.")
    print("✅ AI 응답 성공!")
    print("응답:", response.content[:100] + "...")
    
except Exception as e:
    print("❌ 오류 발생:", str(e))
