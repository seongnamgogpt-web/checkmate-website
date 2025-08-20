"""
이메일 전송 모듈

이 모듈은 분석 결과를 이메일로 전송하는 기능을 제공합니다.
"""

import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import streamlit as st

class EmailSender:
    """
    이메일 전송 클래스
    
    분석 결과를 이메일로 전송하는 기능을 제공합니다.
    """
    
    def __init__(self):
        """
        이메일 전송기 초기화
        """
        # 이메일 설정 (실제 운영시에는 환경 변수로 관리)
        self.smtp_server = "smtp.gmail.com"
        self.smtp_port = 587
        self.sender_email = os.getenv('SENDER_EMAIL', 'checkmate.app@gmail.com')
        self.sender_password = os.getenv('SENDER_PASSWORD', '')
    
    def send_analysis_report(self, analysis_result, recipient_email):
        """
        분석 결과를 이메일로 전송하는 함수
        
        Args:
            analysis_result (dict): 분석 결과
            recipient_email (str): 받는 사람 이메일 주소
            
        Returns:
            bool: 전송 성공 여부
        """
        try:
            # 이메일 내용 생성
            subject = "Check Mate - 수행평가 분석 결과"
            body = self._create_email_body(analysis_result)
            
            # 이메일 메시지 생성
            message = MIMEMultipart()
            message["From"] = self.sender_email
            message["To"] = recipient_email
            message["Subject"] = subject
            
            # 본문 추가
            message.attach(MIMEText(body, "html"))
            
            # 이메일 전송
            if self._send_email(message):
                return True
            else:
                st.error("이메일 전송에 실패했습니다. SMTP 설정을 확인해주세요.")
                return False
                
        except Exception as e:
            st.error(f"이메일 전송 중 오류가 발생했습니다: {str(e)}")
            return False
    
    def _create_email_body(self, analysis_result):
        """
        이메일 본문을 생성하는 함수
        
        Args:
            analysis_result (dict): 분석 결과
            
        Returns:
            str: HTML 형식의 이메일 본문
        """
        total_score = analysis_result.get('total_score', 0)
        max_score = analysis_result.get('max_total_score', 100)
        checklist = analysis_result.get('checklist', [])
        scoring = analysis_result.get('scoring', {})
        suggestions = analysis_result.get('improvement_suggestions', [])
        
        # HTML 본문 생성
        html_body = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .header {{ background-color: #1f77b4; color: white; padding: 20px; text-align: center; }}
                .score-section {{ background-color: #f8f9fa; padding: 20px; margin: 20px 0; border-radius: 10px; }}
                .checklist-section {{ margin: 20px 0; }}
                .scoring-section {{ margin: 20px 0; }}
                .suggestions-section {{ margin: 20px 0; }}
                .condition-item {{ margin: 10px 0; padding: 10px; border-left: 4px solid #ddd; }}
                .fulfilled {{ border-left-color: #28a745; background-color: #d4edda; }}
                .not-fulfilled {{ border-left-color: #dc3545; background-color: #f8d7da; }}
                .score-item {{ margin: 10px 0; padding: 10px; background-color: #e9ecef; border-radius: 5px; }}
                .suggestion-item {{ margin: 10px 0; padding: 10px; background-color: #fff3cd; border-radius: 5px; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>📚 Check Mate - 수행평가 분석 결과</h1>
                <p>분석 일시: {datetime.now().strftime('%Y년 %m월 %d일 %H:%M')}</p>
            </div>
            
            <div class="score-section">
                <h2>📊 총점</h2>
                <h1 style="font-size: 3em; color: #1f77b4; margin: 0;">{total_score}점</h1>
                <p style="font-size: 1.2em; margin: 0;">/ {max_score}점</p>
            </div>
            
            <div class="checklist-section">
                <h2>📋 조건별 충족 여부</h2>
        """
        
        for item in checklist:
            status_class = "fulfilled" if item.get('fulfilled', False) else "not-fulfilled"
            status_icon = "✅" if item.get('fulfilled', False) else "❌"
            status_text = "충족" if item.get('fulfilled', False) else "미충족"
            
            html_body += f"""
                <div class="condition-item {status_class}">
                    <h3>{status_icon} {item.get('condition_number', '')} - {status_text}</h3>
                    <p><strong>조건:</strong> {item.get('content', '')}</p>
                    <p><strong>비고:</strong> {item.get('remarks', '')}</p>
                </div>
            """
        
        html_body += """
            </div>
            
            <div class="scoring-section">
                <h2>📈 세부 점수</h2>
        """
        
        category_names = {
            'content_fidelity': '내용 충실도',
            'condition_fulfillment': '조건 충족도',
            'logical_composition': '논리적 구성',
            'grammar_expression': '문법·표현력'
        }
        
        for category, details in scoring.items():
            category_name = category_names.get(category, category)
            score = details.get('score', 0)
            max_score = details.get('max_score', 0)
            
            html_body += f"""
                <div class="score-item">
                    <h3>{category_name}</h3>
                    <p><strong>점수:</strong> {score}점 / {max_score}점</p>
                </div>
            """
        
        html_body += """
            </div>
            
            <div class="suggestions-section">
                <h2>💡 개선 제안</h2>
        """
        
        if suggestions:
            for i, suggestion in enumerate(suggestions, 1):
                html_body += f"""
                    <div class="suggestion-item">
                        <p><strong>{i}.</strong> {suggestion}</p>
                    </div>
                """
        else:
            html_body += "<p>개선 제안이 없습니다.</p>"
        
        html_body += """
            </div>
            
            <div style="margin-top: 40px; padding: 20px; background-color: #f8f9fa; border-radius: 10px;">
                <p><strong>Check Mate</strong>는 AI 기반 수행평가 초안 검사 시스템입니다.</p>
                <p>더 정확한 분석을 위해 항상 교사의 검토를 받으시기 바랍니다.</p>
            </div>
        </body>
        </html>
        """
        
        return html_body
    
    def _send_email(self, message):
        """
        실제 이메일을 전송하는 함수
        
        Args:
            message: MIME 메시지 객체
            
        Returns:
            bool: 전송 성공 여부
        """
        try:
            # SMTP 서버 연결
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            
            # 로그인 (실제 운영시에는 환경 변수 사용)
            if self.sender_password:
                server.login(self.sender_email, self.sender_password)
            
            # 이메일 전송
            text = message.as_string()
            server.sendmail(self.sender_email, message["To"], text)
            server.quit()
            
            return True
            
        except Exception as e:
            st.error(f"SMTP 오류: {str(e)}")
            return False
    
    def send_test_email(self, recipient_email):
        """
        테스트 이메일을 전송하는 함수
        
        Args:
            recipient_email (str): 받는 사람 이메일 주소
            
        Returns:
            bool: 전송 성공 여부
        """
        test_result = {
            'total_score': 85,
            'max_total_score': 100,
            'checklist': [
                {
                    'condition_number': '조건 1',
                    'content': '글자 수 800자 이상',
                    'fulfilled': True,
                    'remarks': '충족됨'
                }
            ],
            'scoring': {
                'content_fidelity': {'score': 20, 'max_score': 25},
                'condition_fulfillment': {'score': 25, 'max_score': 30},
                'logical_composition': {'score': 20, 'max_score': 25},
                'grammar_expression': {'score': 20, 'max_score': 20}
            },
            'improvement_suggestions': ['테스트 이메일입니다.']
        }
        
        return self.send_analysis_report(test_result, recipient_email) 