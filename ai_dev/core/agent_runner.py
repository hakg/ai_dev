"""
에이전트 러너 — AI 에이전트의 핵심 코어
페르소나(config.json) + 지침(instructions.md) + 스킬(SkillsRegistry)을
조합하여 하나의 완전한 에이전트를 구성하고 실행합니다.
"""
import json
import sys
import os
from typing import Callable, Optional

sys.stdout.reconfigure(encoding='utf-8')


class SkillsRegistry:
    """
    에이전트가 사용할 수 있는 스킬(도구/함수)들을 관리하고 등록하는 클래스입니다.
    이를 통해 LLM의 Function Calling 시스템과 쉽게 연동할 수 있습니다.
    """

    def __init__(self):
        self._skills: dict[str, Callable] = {}

    def register(self, name: str, func: callable) -> None:
        """스킬을 이름과 함께 등록합니다."""
        self._skills[name] = func

    def get(self, name: str) -> Optional[Callable]:
        """이름으로 스킬을 조회합니다."""
        return self._skills.get(name)

    def execute(self, name: str, **kwargs):
        """스킬을 이름으로 찾아 실행합니다."""
        func = self._skills.get(name)
        if func:
            return func(**kwargs)
        return f"[Error] 스킬 '{name}'을(를) 찾을 수 없습니다."

    def list_skills(self) -> list[str]:
        """등록된 모든 스킬 이름을 반환합니다."""
        return list(self._skills.keys())

    def get_skill_descriptions(self) -> str:
        """등록된 모든 스킬의 이름과 독스트링을 반환합니다."""
        descriptions = []
        for name, func in self._skills.items():
            doc = func.__doc__ or "설명 없음"
            descriptions.append(f"- {name}: {doc.strip()}")
        return "\n".join(descriptions)


class AIAgent:
    """
    AI 에이전트의 핵심 코어 클래스.
    
    3분리 아키텍처를 구현합니다:
    1. 페르소나 (config.json) — 에이전트의 정체성, 역할, 목표, 톤
    2. 지침 (instructions.md) — 행동 규칙, 워크플로우, 제약조건
    3. 스킬 (SkillsRegistry) — 실제 실행 가능한 도구/함수
    """

    def __init__(self, config_path: str, instructions_path: str, skills_registry: SkillsRegistry):
        # 1. 페르소나 로드
        with open(config_path, 'r', encoding='utf-8') as f:
            self.persona = json.load(f)

        # 2. 지침 로드
        with open(instructions_path, 'r', encoding='utf-8') as f:
            self.instructions = f.read()

        # 3. 스킬 장착
        self.skills = skills_registry

        # 에이전트 식별 정보
        self.name = self.persona.get("name", "Unknown")
        self.agent_type = self.persona.get("agent_type", "generic")

    def generate_system_prompt(self) -> str:
        """
        LLM에 전달할 최종 시스템 프롬프트를 조립합니다.
        페르소나 데이터 + 마크다운 지침 + 사용 가능한 스킬 목록을 결합합니다.
        """
        prompt_parts = [
            f"=== 에이전트 페르소나 ===",
            f"이름: {self.persona.get('name', 'N/A')}",
            f"역할: {self.persona.get('role', 'N/A')}",
            f"목표: {self.persona.get('goal', 'N/A')}",
            f"톤: {self.persona.get('tone', 'N/A')}",
            "",
            "=== 수행 지침 ===",
            self.instructions,
            "",
            "=== 사용 가능한 스킬 ===",
            self.skills.get_skill_descriptions(),
        ]
        return "\n".join(prompt_parts)

    def run(self, user_input: str, context: dict = None) -> str:
        """
        에이전트를 실행합니다.
        
        시뮬레이션 모드에서는 에이전트 타입에 따라
        규칙 기반으로 산출물을 생성합니다.
        
        향후 LLM API 연동 시 이 메서드를 확장합니다.
        
        Args:
            user_input: 사용자 또는 이전 에이전트의 입력
            context: 이전 단계에서 전달된 컨텍스트
            
        Returns:
            에이전트의 산출물 (문자열)
        """
        context = context or {}
        emoji = self._get_emoji()

        print(f"\n{'='*50}")
        print(f"[{emoji} {self.name}] 에이전트 구동")
        print(f"{'='*50}")

        # 시스템 프롬프트 생성 (LLM 연동 시 사용)
        system_prompt = self.generate_system_prompt()

        # 에이전트 타입별 처리 로직
        handler = self._get_handler()
        result = handler(user_input, context)

        print(f"[{emoji} {self.name}] 작업 완료")
        return result

    def _get_handler(self) -> callable:
        """에이전트 타입에 따른 핸들러를 반환합니다."""
        handlers = {
            "pm":        self._handle_pm,
            "planner":   self._handle_planner,
            "architect": self._handle_architect,
            "coder":     self._handle_coder,
            "reviewer":  self._handle_reviewer,
            "tester":    self._handle_tester,
            "designer":  self._handle_designer,
        }
        return handlers.get(self.agent_type, self._handle_generic)

    def _get_emoji(self) -> str:
        """에이전트 타입에 맞는 이모지를 반환합니다."""
        emojis = {
            "pm": "🎯", "planner": "📝", "architect": "🏗️",
            "coder": "💻", "reviewer": "🔍", "tester": "🧪", "designer": "🎨",
        }
        return emojis.get(self.agent_type, "🤖")

    # ================================================================
    # 에이전트 타입별 핸들러 (시뮬레이션 모드)
    # 향후 LLM API 연동 시 이 부분을 API 호출로 교체합니다.
    # ================================================================

    def _handle_pm(self, user_input: str, context: dict) -> str:
        """PM: 작업을 분석하고 파이프라인을 결정합니다."""
        # UI 관련 키워드 감지
        ui_keywords = ["웹", "앱", "UI", "화면", "페이지", "프론트엔드", "디자인", "인터페이스"]
        has_ui = any(keyword in user_input for keyword in ui_keywords)
        pipeline_type = "UI 포함 파이프라인" if has_ui else "기본 파이프라인"

        result = f"""📋 프로젝트 분석 완료
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📌 프로젝트명: {self._extract_project_name(user_input)}
💡 원본 아이디어: {user_input}
🔄 선택된 파이프라인: {pipeline_type}
📊 UI 요소 감지: {"✅ 예" if has_ui else "❌ 아니오"}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
▶ 다음 단계: Planner에게 기획서 작성을 위임합니다."""
        print(result)
        return result

    def _handle_planner(self, user_input: str, context: dict) -> str:
        """Planner: 아이디어를 PRD(기획서)로 변환합니다."""
        idea = context.get("idea", user_input)

        # PRD 템플릿 기반 생성 (시뮬레이션)
        prd = self.skills.execute("generate_prd", idea=idea)
        print(f"  📄 PRD 문서 생성 완료 ({len(prd)}자)")
        return prd

    def _handle_architect(self, user_input: str, context: dict) -> str:
        """Architect: PRD를 기반으로 설계서를 작성합니다."""
        prd = context.get("prd", "")
        idea = context.get("idea", user_input)

        design_doc = self.skills.execute("generate_design_doc", idea=idea, prd=prd)
        print(f"  📐 설계 문서 생성 완료 ({len(design_doc)}자)")
        return design_doc

    def _handle_coder(self, user_input: str, context: dict) -> str:
        """Coder: 설계서를 기반으로 코드를 작성합니다."""
        architecture = context.get("architecture", "")
        prd = context.get("prd", "")
        idea = context.get("idea", user_input)

        code_output = f"""# ============================================================
# 프로젝트: {self._extract_project_name(idea)}
# 생성 기반: Architect 설계서 + Planner PRD
# ============================================================

\"\"\"
[Coder 에이전트 산출물]

📌 구현 요약:
- 아이디어: {idea[:60]}...
- PRD 기반 기능 구현
- 설계서의 아키텍처와 데이터 모델 준수

📁 생성된 파일 구조:
├── main.py          (진입점)
├── models/          (데이터 모델)
├── services/        (비즈니스 로직)
├── routes/          (API 엔드포인트)
└── utils/           (유틸리티)

⚠️ 현재 시뮬레이션 모드입니다.
   LLM API 연동 시 실제 코드가 생성됩니다.
\"\"\"

# 예시 코드 구조 (시뮬레이션)
class Application:
    \"\"\"메인 애플리케이션 클래스\"\"\"
    
    def __init__(self):
        self.name = "{self._extract_project_name(idea)}"
        self.version = "1.0.0"
    
    def initialize(self):
        \"\"\"애플리케이션을 초기화합니다.\"\"\"
        print(f"{{self.name}} v{{self.version}} 초기화 완료")
    
    def run(self):
        \"\"\"애플리케이션을 실행합니다.\"\"\"
        self.initialize()
        print(f"{{self.name}} 실행 중...")


if __name__ == "__main__":
    app = Application()
    app.run()
"""
        print(f"  📝 코드 생성 완료 ({len(code_output)}자)")
        return code_output

    def _handle_reviewer(self, user_input: str, context: dict) -> str:
        """Reviewer: 코드를 리뷰하고 결과를 반환합니다."""
        code = context.get("code", "")
        architecture = context.get("architecture", "")

        # 코드 분석 스킬 호출
        analysis = self.skills.execute("analyze_code", code=code)

        review_result = f"""🔍 코드 리뷰 결과
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 코드 분석:
{analysis}

📋 리뷰 체크리스트:
  ✅ [보안] 하드코딩된 비밀번호/API 키 없음
  ✅ [성능] 명백한 성능 병목 없음
  ✅ [에러처리] 기본 예외 처리 구조 확인
  🟡 [설계 준수] 설계서 대비 구현 범위 확인 필요
  ✅ [코드 중복] 중복 코드 없음

🏷️ 심각도 분류:
  🔴 Critical: 0건
  🟡 Warning: 1건 (설계서 대비 구현 범위 확인)
  🟢 Suggestion: 0건

📌 최종 판정: ✅ APPROVED (승인)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
▶ Tester에게 테스트 단계로 넘어갑니다."""
        print(review_result)
        return review_result

    def _handle_tester(self, user_input: str, context: dict) -> str:
        """Tester: 코드에 대한 테스트를 실행합니다."""
        code = context.get("code", "")

        test_result = f"""🧪 테스트 실행 결과
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 테스트 요약:
  ✅ 단위 테스트 (Unit):      5/5 통과
  ✅ 통합 테스트 (Integration): 3/3 통과
  ⬜ E2E 테스트:              해당 없음

📈 커버리지: 85% (목표 80% 달성)

📋 테스트 상세:
  ✅ test_application_init .............. PASSED
  ✅ test_application_run ............... PASSED
  ✅ test_application_name .............. PASSED
  ✅ test_application_version ........... PASSED
  ✅ test_application_initialize ........ PASSED
  ✅ test_integration_full_flow ......... PASSED
  ✅ test_integration_error_handling .... PASSED
  ✅ test_integration_config_load ....... PASSED

📌 최종 판정: ✅ ALL TESTS PASSED
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
▶ PM에게 완료 보고합니다."""
        print(test_result)
        return test_result

    def _handle_designer(self, user_input: str, context: dict) -> str:
        """Designer: UI/UX 설계를 수행합니다."""
        prd = context.get("prd", "")
        idea = context.get("idea", user_input)

        design = f"""🎨 UI/UX 설계서
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📌 디자인 시스템:

🎨 컬러 팔레트:
  - Primary:   #6366F1 (인디고)
  - Secondary: #EC4899 (핑크)
  - Background: #0F172A (다크 네이비)
  - Surface:   #1E293B (슬레이트)
  - Text:      #F8FAFC (화이트)

📝 타이포그래피:
  - 제목: Inter Bold 24px
  - 본문: Inter Regular 16px
  - 캡션: Inter Light 12px

📱 레이아웃: 
  - 모바일 퍼스트 반응형 (320px ~ 1440px)
  - 그리드: 12컬럼 시스템
  - 간격: 8px 배수 시스템

🧩 주요 컴포넌트:
  - 헤더 (네비게이션 + 로고)
  - 사이드바 (좌측 메뉴)
  - 메인 콘텐츠 영역
  - 카드 컴포넌트
  - 버튼 (Primary, Secondary, Ghost)
  - 입력 필드
  - 모달 / 다이얼로그

♿ 접근성:
  - WCAG 2.1 AA 기준 준수
  - 색 대비 비율 4.5:1 이상
  - 키보드 네비게이션 지원
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"""
        print(f"  🎨 UI/UX 설계 완료")
        return design

    def _handle_generic(self, user_input: str, context: dict) -> str:
        """기본 핸들러 (알 수 없는 에이전트 타입)"""
        return f"[{self.name}] 아직 이 에이전트의 파이프라인이 구현되지 않았습니다. 입력: {user_input[:50]}..."

    @staticmethod
    def _extract_project_name(idea: str) -> str:
        """아이디어에서 프로젝트 이름을 추출합니다 (간단한 규칙 기반)."""
        # 첫 50자를 프로젝트 이름으로 사용
        name = idea[:50].strip()
        # 특수문자 제거하여 파일명에 안전하게
        safe_name = "".join(c for c in name if c.isalnum() or c in " _-가-힣")
        return safe_name if safe_name else "새로운 프로젝트"
