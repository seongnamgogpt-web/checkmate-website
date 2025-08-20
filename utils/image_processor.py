"""
이미지 처리 모듈

이 모듈은 업로드된 파일(이미지, 텍스트 파일)에서 텍스트를 추출하는 기능을 제공합니다.
"""

import io
import pytesseract
from PIL import Image
import streamlit as st

def process_uploaded_file(uploaded_file):
    """
    업로드된 파일에서 텍스트를 추출하는 함수
    
    Args:
        uploaded_file: Streamlit의 uploaded file 객체
        
    Returns:
        str: 추출된 텍스트
    """
    try:
        # 파일 타입 확인
        file_type = uploaded_file.type
        
        if file_type.startswith('image/'):
            # 이미지 파일 처리
            return process_image_file(uploaded_file)
        elif file_type in ['text/plain', 'application/octet-stream']:
            # 텍스트 파일 처리
            return process_text_file(uploaded_file)
        else:
            st.error(f"지원하지 않는 파일 형식입니다: {file_type}")
            return ""
            
    except Exception as e:
        st.error(f"파일 처리 중 오류가 발생했습니다: {str(e)}")
        return ""

def process_image_file(uploaded_file):
    """
    이미지 파일에서 텍스트를 추출하는 함수
    
    Args:
        uploaded_file: 업로드된 이미지 파일
        
    Returns:
        str: 추출된 텍스트
    """
    try:
        # 이미지 로드
        image = Image.open(uploaded_file)
        
        # OCR을 사용하여 텍스트 추출
        text = pytesseract.image_to_string(image, lang='kor+eng')
        
        if not text.strip():
            st.warning("이미지에서 텍스트를 추출할 수 없습니다. 이미지 품질을 확인해주세요.")
            return ""
            
        return text.strip()
        
    except Exception as e:
        st.error(f"이미지 처리 중 오류가 발생했습니다: {str(e)}")
        return ""

def process_text_file(uploaded_file):
    """
    텍스트 파일에서 텍스트를 추출하는 함수
    
    Args:
        uploaded_file: 업로드된 텍스트 파일
        
    Returns:
        str: 추출된 텍스트
    """
    try:
        # 텍스트 파일 읽기
        text = uploaded_file.read().decode('utf-8')
        return text.strip()
        
    except UnicodeDecodeError:
        try:
            # UTF-8로 읽기 실패시 다른 인코딩 시도
            uploaded_file.seek(0)  # 파일 포인터를 처음으로 되돌리기
            text = uploaded_file.read().decode('cp949')
            return text.strip()
        except Exception as e:
            st.error(f"텍스트 파일 인코딩 오류: {str(e)}")
            return ""
    except Exception as e:
        st.error(f"텍스트 파일 처리 중 오류가 발생했습니다: {str(e)}")
        return "" 