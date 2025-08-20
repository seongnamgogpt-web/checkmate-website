"""
Check Mate - 수행평가 초안 검사 웹 애플리케이션

이 애플리케이션은 학생들이 수행평가 초안이 평가 조건에 부합하는지 
자동으로 검사하는 AI 기반 웹 도구입니다.

고등학생도 이해할 수 있도록 간단한 설명을 포함했습니다.
"""

import streamlit as st
import os
from dotenv import load_dotenv
import pandas as pd

# 사용자 정의 모듈들 가져오기
from utils.image_processor import process_uploaded_file
from utils.ai_analyzer import PerformanceAnalyzer
from utils.email_sender import EmailSender

# 환경 변수 로드
load_dotenv()

# Google Gemini API 키 직접 설정 (환경 변수가 없는 경우)
if not os.getenv('GOOGLE_API_KEY'):
    os.environ['GOOGLE_API_KEY'] = "AIzaSyAlUl_2hPSCrCzR9VMnmvfh4JLVR2K7gnE"

def main():
    """
    메인 애플리케이션 함수
    
    이 함수는 웹 애플리케이션의 전체적인 흐름을 관리합니다.
    """
    
    # 페이지 설정
    st.set_page_config(
        page_title="Check Mate - 수행평가 초안 검사",
        page_icon="📚",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # CSS 스타일 적용
    st.markdown("""
    <style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        color: #1f77b4;
        margin-bottom: 2rem;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #2c3e50;
        margin-bottom: 1rem;
    }
    .info-box {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
        margin: 1rem 0;
    }
    .success-box {
        background-color: #d4edda;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #28a745;
        margin: 1rem 0;
    }
    .warning-box {
        background-color: #fff3cd;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #ffc107;
        margin: 1rem 0;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # 메인 헤더
    st.markdown('<h1 class="main-header">📚 Check Mate</h1>', unsafe_allow_html=True)
    st.markdown('<h2 class="sub-header" style="text-align: center;">수행평가 초안 자동 검사 시스템</h2>', unsafe_allow_html=True)
    
    # 사이드바에 정보 표시
    with st.sidebar:
        st.markdown("### ℹ️ 사용법 안내")
        st.markdown("""
        1. **수행평가 요구조건** 입력
        2. **수행평가 초안** 입력  
        3. **분석 시작** 버튼 클릭
        4. **결과 확인** 및 개선점 파악
        """)
        
        st.markdown("### 📝 입력 방법")
        st.markdown("""
        - **직접 입력**: 텍스트 영역에 직접 작성
        - **파일 업로드**: .txt, .md 파일 업로드
        - **이미지 업로드**: 사진으로 촬영한 문서 업로드
        """)
        
        st.markdown("### ⚠️ 주의사항")
        st.markdown("""
        - Google Gemini API 키가 필요합니다
        - 이미지 품질이 좋을수록 정확도가 높습니다
        - 개인정보가 포함된 내용은 주의해서 입력하세요
        """)
    
    # 탭 생성
    tab1, tab2, tab3 = st.tabs(["📝 입력", "📊 분석 결과", "📧 결과 공유"])
    
    with tab1:
        input_tab()
    
    with tab2:
        result_tab()
    
    with tab3:
        share_tab()

def input_tab():
    """
    입력 탭을 처리하는 함수
    
    사용자가 수행평가 요구조건과 초안을 입력하는 화면을 제공합니다.
    """
    
    st.markdown('<h3 class="sub-header">📝 수행평가 정보 입력</h3>', unsafe_allow_html=True)
    
    # 두 개의 컬럼으로 나누기
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📋 수행평가 요구조건")
        
        # 조건 입력 방법 선택
        condition_input_method = st.radio(
            "조건 입력 방법을 선택하세요:",
            ["직접 입력", "파일 업로드", "이미지 업로드"],
            key="condition_method"
        )
        
        conditions_text = ""
        
        if condition_input_method == "직접 입력":
            # 예시 조건 표시
            with st.expander("💡 조건 입력 예시"):
                st.markdown("""
                ```
                조건 1. 글자 수 800자 이상 1200자 이하 (띄어쓰기 포함)
                조건 2. 대륙이동설 제안자와 핵심 주장을 포함할것
                조건 3. 대륙이동설의 한계를 서술할것
                조건 4. 해저확장설의 등장과 주요 증거를 포함할것
                조건 5. 서론-본론-결론 구조로 작성할것
                ```
                """)
            
            conditions_text = st.text_area(
                "수행평가 요구조건을 입력하세요:",
                height=200,
                placeholder="조건 1. [조건 내용]\n조건 2. [조건 내용]\n..."
            )
        
        elif condition_input_method == "파일 업로드":
            uploaded_condition_file = st.file_uploader(
                "조건이 포함된 파일을 업로드하세요:",
                type=['txt', 'md'],
                key="condition_file"
            )
            if uploaded_condition_file:
                conditions_text = process_uploaded_file(uploaded_condition_file)
                st.text_area("추출된 조건:", conditions_text, height=200, disabled=True)
        
        elif condition_input_method == "이미지 업로드":
            uploaded_condition_image = st.file_uploader(
                "조건이 포함된 이미지를 업로드하세요:",
                type=['png', 'jpg', 'jpeg', 'gif', 'bmp'],
                key="condition_image"
            )
            if uploaded_condition_image:
                conditions_text = process_uploaded_file(uploaded_condition_image)
                st.text_area("추출된 조건:", conditions_text, height=200, disabled=True)
    
    with col2:
        st.markdown("### 📄 수행평가 초안")
        
        # 초안 입력 방법 선택
        draft_input_method = st.radio(
            "초안 입력 방법을 선택하세요:",
            ["직접 입력", "파일 업로드", "이미지 업로드"],
            key="draft_method"
        )
        
        draft_text = ""
        
        if draft_input_method == "직접 입력":
            
            draft_text = st.text_area(
                "수행평가 초안을 입력하세요:",
                height=300,
                placeholder="여기에 수행평가 초안을 작성하세요..."
            )
        
        elif draft_input_method == "파일 업로드":
            uploaded_draft_file = st.file_uploader(
                "초안이 포함된 파일을 업로드하세요:",
                type=['txt', 'md'],
                key="draft_file"
            )
            if uploaded_draft_file:
                draft_text = process_uploaded_file(uploaded_draft_file)
                st.text_area("추출된 초안:", draft_text, height=300, disabled=True)
        
        elif draft_input_method == "이미지 업로드":
            uploaded_draft_image = st.file_uploader(
                "초안이 포함된 이미지를 업로드하세요:",
                type=['png', 'jpg', 'jpeg', 'gif', 'bmp'],
                key="draft_image"
            )
            if uploaded_draft_image:
                draft_text = process_uploaded_file(uploaded_draft_image)
                st.text_area("추출된 초안:", draft_text, height=300, disabled=True)
    
    # 분석 시작 버튼
    st.markdown("---")
    
    if st.button("🚀 분석 시작", type="primary", use_container_width=True):
        if conditions_text.strip() and draft_text.strip():
            # 세션 상태에 데이터 저장
            st.session_state.conditions = conditions_text
            st.session_state.draft = draft_text
            
            # 분석 실행
            with st.spinner("AI가 수행평가를 분석하고 있습니다..."):
                analyzer = PerformanceAnalyzer()
                result = analyzer.analyze_performance(conditions_text, draft_text)
                st.session_state.analysis_result = result
            
            st.success("분석이 완료되었습니다! '📊 분석 결과' 탭에서 확인하세요.")
            st.balloons()
        else:
            st.error("수행평가 요구조건과 초안을 모두 입력해주세요.")

def result_tab():
    """
    분석 결과 탭을 처리하는 함수
    
    AI 분석 결과를 보기 좋게 표시합니다.
    """
    
    st.markdown('<h3 class="sub-header">📊 분석 결과</h3>', unsafe_allow_html=True)
    
    # 분석 결과가 있는지 확인
    if 'analysis_result' not in st.session_state:
        st.info("먼저 '📝 입력' 탭에서 분석을 시작해주세요.")
        return
    
    result = st.session_state.analysis_result
    
    # 총점 표시
    total_score = result.get('total_score', 0)
    max_score = result.get('max_total_score', 100)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown(f"""
        <div style="text-align: center; padding: 2rem; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 1rem; color: white;">
            <h2>총점</h2>
            <h1 style="font-size: 4rem; margin: 0;">{total_score}점</h1>
            <p style="font-size: 1.2rem; margin: 0;">/ {max_score}점</p>
        </div>
        """, unsafe_allow_html=True)
    
    # 체크리스트 표시
    st.markdown("### 📋 조건별 충족 여부")
    
    checklist = result.get('checklist', [])
    if checklist:
        # DataFrame으로 변환해서 표시
        checklist_data = []
        for item in checklist:
            checklist_data.append({
                '조건': item.get('condition_number', ''),
                '내용': item.get('content', ''),
                '충족 여부': '✅ 충족' if item.get('fulfilled', False) else '❌ 미충족',
                '비고': item.get('remarks', '')
            })
        
        df_checklist = pd.DataFrame(checklist_data)
        st.dataframe(df_checklist, use_container_width=True)
    
    # 세부 점수 표시
    st.markdown("### 📈 세부 점수")
    
    scoring = result.get('scoring', {})
    if scoring:
        # 점수 데이터 준비
        score_data = []
        for category, details in scoring.items():
            category_name = get_category_name(category)
            score = details.get('score', 0)
            max_score = details.get('max_score', 0)
            evaluation = details.get('evaluation', '')
            
            score_data.append({
                '평가 항목': category_name,
                '점수': f"{score}점 / {max_score}점",
                '평가 내용': evaluation
            })
        
        df_scoring = pd.DataFrame(score_data)
        st.dataframe(df_scoring, use_container_width=True)
    
    # 개선 제안 표시
    suggestions = result.get('improvement_suggestions', [])
    if suggestions:
        st.markdown("### 💡 개선 제안")
        for i, suggestion in enumerate(suggestions, 1):
            st.markdown(f"**{i}.** {suggestion}")

def share_tab():
    """
    결과 공유 탭을 처리하는 함수
    
    분석 결과를 이메일로 공유하는 기능을 제공합니다.
    """
    
    st.markdown('<h3 class="sub-header">📧 결과 공유</h3>', unsafe_allow_html=True)
    
    # 분석 결과가 있는지 확인
    if 'analysis_result' not in st.session_state:
        st.info("먼저 '📝 입력' 탭에서 분석을 시작해주세요.")
        return
    
    st.markdown("""
    <div class="info-box">
        <strong>📧 이메일 공유 기능</strong><br>
        분석 결과를 이메일로 받아보거나 다른 사람과 공유할 수 있습니다.
    </div>
    """, unsafe_allow_html=True)
    
    # 이메일 입력
    recipient_email = st.text_input(
        "받는 사람 이메일 주소:",
        placeholder="example@email.com"
    )
    
    # 공유 버튼
    if st.button("📧 결과 공유하기", type="primary"):
        if recipient_email and '@' in recipient_email:
            email_sender = EmailSender()
            success = email_sender.send_analysis_report(
                st.session_state.analysis_result,
                recipient_email
            )
            
            if success:
                st.success("이메일이 성공적으로 전송되었습니다!")
        else:
            st.error("올바른 이메일 주소를 입력해주세요.")

def get_category_name(category):
    """
    카테고리 영문명을 한글명으로 변환하는 함수
    
    Args:
        category (str): 카테고리 영문명
        
    Returns:
        str: 카테고리 한글명
    """
    category_names = {
        'content_fidelity': '내용 충실도',
        'condition_fulfillment': '조건 충족도',
        'logical_composition': '논리적 구성',
        'grammar_expression': '문법·표현력'
    }
    
    return category_names.get(category, category)

if __name__ == "__main__":
    main()
