"""
AI 분석 모듈

이 모듈은 Google Gemini API를 사용하여 수행평가 초안을 분석하는 기능을 제공합니다.
"""

import os
import google.generativeai as genai
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.schema import HumanMessage
import json
import re

class PerformanceAnalyzer:
    """
    수행평가 분석기 클래스
    
    Google Gemini API를 사용하여 수행평가 초안을 분석합니다.
    """
    
    def __init__(self):
        """
        분석기 초기화
        """
        # Google API 키 설정
        api_key = os.getenv('GOOGLE_API_KEY')
        if not api_key:
            raise ValueError("GOOGLE_API_KEY 환경 변수가 설정되지 않았습니다.")
        
        # Gemini 모델 설정
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-pro')
        
        # LangChain 모델 설정
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-pro",
            google_api_key=api_key,
            temperature=0.3
        )
    
    def analyze_performance(self, conditions_text, draft_text):
        """
        수행평가 초안을 분석하는 메인 함수
        
        Args:
            conditions_text (str): 수행평가 요구조건
            draft_text (str): 수행평가 초안
            
        Returns:
            dict: 분석 결과
        """
        try:
            # 1. 조건 파싱
            conditions = self._parse_conditions(conditions_text)
            
            # 2. 체크리스트 생성
            checklist = self._create_checklist(conditions, draft_text)
            
            # 3. 세부 점수 계산
            scoring = self._calculate_scoring(conditions, draft_text)
            
            # 4. 총점 계산
            total_score = sum(item['score'] for item in scoring.values())
            max_total_score = sum(item['max_score'] for item in scoring.values())
            
            # 5. 개선 제안 생성
            improvement_suggestions = self._generate_improvement_suggestions(
                conditions, draft_text, checklist, scoring
            )
            
            return {
                'conditions': conditions,
                'checklist': checklist,
                'scoring': scoring,
                'total_score': total_score,
                'max_total_score': max_total_score,
                'improvement_suggestions': improvement_suggestions
            }
            
        except Exception as e:
            return {
                'error': f"분석 중 오류가 발생했습니다: {str(e)}",
                'conditions': [],
                'checklist': [],
                'scoring': {},
                'total_score': 0,
                'max_total_score': 100,
                'improvement_suggestions': []
            }
    
    def _parse_conditions(self, conditions_text):
        """
        조건 텍스트를 파싱하는 함수
        
        Args:
            conditions_text (str): 조건 텍스트
            
        Returns:
            list: 파싱된 조건 리스트
        """
        conditions = []
        lines = conditions_text.strip().split('\n')
        
        for line in lines:
            line = line.strip()
            if line and (line.startswith('조건') or line.startswith('조건')):
                # 조건 번호와 내용 분리
                match = re.match(r'조건\s*(\d+)\.?\s*(.+)', line)
                if match:
                    condition_num = match.group(1)
                    condition_content = match.group(2).strip()
                    conditions.append({
                        'number': condition_num,
                        'content': condition_content
                    })
        
        return conditions
    
    def _create_checklist(self, conditions, draft_text):
        """
        체크리스트를 생성하는 함수
        
        Args:
            conditions (list): 파싱된 조건 리스트
            draft_text (str): 수행평가 초안
            
        Returns:
            list: 체크리스트
        """
        checklist = []
        
        for condition in conditions:
            # 각 조건에 대해 AI가 충족 여부를 판단
            prompt = f"""
            다음 조건이 수행평가 초안에서 충족되었는지 판단해주세요.
            
            조건: {condition['content']}
            
            수행평가 초안:
            {draft_text}
            
            다음 JSON 형식으로 응답해주세요:
            {{
                "fulfilled": true/false,
                "remarks": "충족 여부에 대한 간단한 설명"
            }}
            """
            
            try:
                response = self.model.generate_content(prompt)
                result = json.loads(response.text)
                
                checklist.append({
                    'condition_number': f"조건 {condition['number']}",
                    'content': condition['content'],
                    'fulfilled': result.get('fulfilled', False),
                    'remarks': result.get('remarks', '')
                })
            except:
                # AI 응답 실패시 기본값 설정
                checklist.append({
                    'condition_number': f"조건 {condition['number']}",
                    'content': condition['content'],
                    'fulfilled': False,
                    'remarks': 'AI 분석 실패'
                })
        
        return checklist
    
    def _calculate_scoring(self, conditions, draft_text):
        """
        세부 점수를 계산하는 함수
        
        Args:
            conditions (list): 파싱된 조건 리스트
            draft_text (str): 수행평가 초안
            
        Returns:
            dict: 세부 점수
        """
        scoring = {
            'content_fidelity': {'score': 0, 'max_score': 25, 'evaluation': ''},
            'condition_fulfillment': {'score': 0, 'max_score': 30, 'evaluation': ''},
            'logical_composition': {'score': 0, 'max_score': 25, 'evaluation': ''},
            'grammar_expression': {'score': 0, 'max_score': 20, 'evaluation': ''}
        }
        
        # 조건 충족도 계산
        fulfilled_count = sum(1 for condition in conditions if self._check_condition_fulfillment(condition, draft_text))
        condition_score = min(30, (fulfilled_count / len(conditions)) * 30) if conditions else 0
        scoring['condition_fulfillment']['score'] = int(condition_score)
        
        # 내용 충실도 평가
        content_score = self._evaluate_content_fidelity(draft_text)
        scoring['content_fidelity']['score'] = content_score
        
        # 논리적 구성 평가
        logic_score = self._evaluate_logical_composition(draft_text)
        scoring['logical_composition']['score'] = logic_score
        
        # 문법·표현력 평가
        grammar_score = self._evaluate_grammar_expression(draft_text)
        scoring['grammar_expression']['score'] = grammar_score
        
        return scoring
    
    def _check_condition_fulfillment(self, condition, draft_text):
        """
        개별 조건의 충족 여부를 확인하는 함수
        
        Args:
            condition (dict): 조건 정보
            draft_text (str): 수행평가 초안
            
        Returns:
            bool: 충족 여부
        """
        # 간단한 키워드 매칭으로 충족 여부 판단
        condition_content = condition['content'].lower()
        draft_lower = draft_text.lower()
        
        # 글자 수 조건 확인
        if '글자' in condition_content and ('자' in condition_content or '수' in condition_content):
            char_count = len(draft_text.replace(' ', ''))
            numbers = re.findall(r'\d+', condition_content)
            if len(numbers) >= 2:
                min_chars, max_chars = int(numbers[0]), int(numbers[1])
                return min_chars <= char_count <= max_chars
        
        # 구조 조건 확인
        if '구조' in condition_content or '서론' in condition_content:
            return '서론' in draft_lower and '본론' in draft_lower and '결론' in draft_lower
        
        # 키워드 포함 여부 확인
        keywords = re.findall(r'[가-힣a-zA-Z]+', condition_content)
        return any(keyword in draft_lower for keyword in keywords if len(keyword) > 1)
    
    def _evaluate_content_fidelity(self, draft_text):
        """
        내용 충실도를 평가하는 함수
        
        Args:
            draft_text (str): 수행평가 초안
            
        Returns:
            int: 점수 (0-25)
        """
        # 간단한 평가 기준
        score = 15  # 기본 점수
        
        # 글자 수에 따른 보너스
        char_count = len(draft_text.replace(' ', ''))
        if char_count >= 800:
            score += 5
        if char_count >= 1000:
            score += 5
        
        return min(25, score)
    
    def _evaluate_logical_composition(self, draft_text):
        """
        논리적 구성을 평가하는 함수
        
        Args:
            draft_text (str): 수행평가 초안
            
        Returns:
            int: 점수 (0-25)
        """
        score = 15  # 기본 점수
        
        # 구조적 요소 확인
        if '서론' in draft_text or '도입' in draft_text:
            score += 3
        if '본론' in draft_text or '전개' in draft_text:
            score += 4
        if '결론' in draft_text or '마무리' in draft_text:
            score += 3
        
        return min(25, score)
    
    def _evaluate_grammar_expression(self, draft_text):
        """
        문법·표현력을 평가하는 함수
        
        Args:
            draft_text (str): 수행평가 초안
            
        Returns:
            int: 점수 (0-20)
        """
        score = 12  # 기본 점수
        
        # 문장 수에 따른 보너스
        sentences = draft_text.split('.')
        if len(sentences) >= 10:
            score += 4
        if len(sentences) >= 15:
            score += 4
        
        return min(20, score)
    
    def _generate_improvement_suggestions(self, conditions, draft_text, checklist, scoring):
        """
        개선 제안을 생성하는 함수
        
        Args:
            conditions (list): 파싱된 조건 리스트
            draft_text (str): 수행평가 초안
            checklist (list): 체크리스트
            scoring (dict): 세부 점수
            
        Returns:
            list: 개선 제안 리스트
        """
        suggestions = []
        
        # 미충족 조건에 대한 제안
        for item in checklist:
            if not item['fulfilled']:
                suggestions.append(f"조건 {item['condition_number']}: {item['content']} - 이 조건을 충족하도록 내용을 보완해주세요.")
        
        # 점수가 낮은 영역에 대한 제안
        if scoring['content_fidelity']['score'] < 15:
            suggestions.append("내용을 더 구체적이고 상세하게 작성해주세요.")
        
        if scoring['logical_composition']['score'] < 15:
            suggestions.append("서론-본론-결론 구조를 명확히 하여 논리적 흐름을 개선해주세요.")
        
        if scoring['grammar_expression']['score'] < 12:
            suggestions.append("문장을 더 명확하고 정확하게 작성해주세요.")
        
        return suggestions 