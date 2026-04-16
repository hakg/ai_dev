"""
AI 에이전트 팀 시스템 — 전역 설정
프로젝트 전체에서 사용하는 경로, 상수, 설정값을 한 곳에서 관리합니다.
"""
import os

# ============================================================
# 경로 설정
# ============================================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
AGENTS_DIR = os.path.join(BASE_DIR, "agents")
SKILLS_DIR = os.path.join(BASE_DIR, "skills")
SHARED_DIR = os.path.join(BASE_DIR, "shared")
TEMPLATES_DIR = os.path.join(SHARED_DIR, "templates")
CONTEXT_DIR = os.path.join(SHARED_DIR, "context")
OUTPUT_DIR = os.path.join(BASE_DIR, "output")

# ============================================================
# 에이전트 설정
# ============================================================
# 에이전트 이름 → 폴더 매핑
AGENT_FOLDERS = {
    "pm":        "pm_agent",
    "planner":   "planner_agent",
    "architect": "architect_agent",
    "coder":     "coder_agent",
    "reviewer":  "reviewer_agent",
    "tester":    "tester_agent",
    "designer":  "designer_agent",
}

# ============================================================
# 파이프라인 설정
# ============================================================
# 기본 파이프라인 순서 (PM이 이 순서로 에이전트를 호출)
DEFAULT_PIPELINE = ["planner", "architect", "coder", "reviewer", "tester"]

# UI가 포함된 프로젝트일 경우의 파이프라인
UI_PIPELINE = ["planner", "architect", "designer", "coder", "reviewer", "tester"]

# 피드백 루프 최대 반복 횟수 (Reviewer/Tester 반려 시)
MAX_FEEDBACK_LOOPS = 3

# ============================================================
# 출력 설정
# ============================================================
# 콘솔 출력 시 사용할 이모지 태그
AGENT_EMOJI = {
    "pm":        "🎯",
    "planner":   "📝",
    "architect": "🏗️",
    "coder":     "💻",
    "reviewer":  "🔍",
    "tester":    "🧪",
    "designer":  "🎨",
}

# ============================================================
# 디렉토리 자동 생성
# ============================================================
for dir_path in [SHARED_DIR, TEMPLATES_DIR, CONTEXT_DIR, OUTPUT_DIR]:
    os.makedirs(dir_path, exist_ok=True)
