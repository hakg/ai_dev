"""
AI 에이전트 팀 시스템 — 메인 진입점
사용자의 아이디어를 입력받아 전체 에이전트 팀 파이프라인을 실행합니다.

사용법:
    python main.py                          # 대화형 모드
    python main.py "할 일 관리 앱을 만들어줘"  # 직접 입력 모드
"""
import sys
import os

# UTF-8 인코딩 설정
sys.stdout.reconfigure(encoding='utf-8')

# 프로젝트 루트를 모듈 탐색 경로에 추가
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import (
    AGENTS_DIR, CONTEXT_DIR, OUTPUT_DIR,
    AGENT_FOLDERS, DEFAULT_PIPELINE, UI_PIPELINE,
    MAX_FEEDBACK_LOOPS, AGENT_EMOJI
)
from core.agent_runner import AIAgent, SkillsRegistry
from core.orchestrator import Orchestrator

# Skills 임포트
from skills.file_operations import read_file, write_code, list_directory
from skills.code_analysis import analyze_code, count_lines
from skills.test_runner import run_tests, generate_test_report
from skills.document_generator import generate_prd, generate_design_doc


def setup_skills() -> SkillsRegistry:
    """모든 스킬을 레지스트리에 등록합니다."""
    registry = SkillsRegistry()
    
    # 파일 조작 스킬
    registry.register("read_file", read_file)
    registry.register("write_code", write_code)
    registry.register("list_directory", list_directory)
    
    # 코드 분석 스킬
    registry.register("analyze_code", analyze_code)
    registry.register("count_lines", count_lines)
    
    # 테스트 스킬
    registry.register("run_tests", run_tests)
    registry.register("generate_test_report", generate_test_report)
    
    # 문서 생성 스킬
    registry.register("generate_prd", generate_prd)
    registry.register("generate_design_doc", generate_design_doc)
    
    print(f"  ✅ 스킬 {len(registry.list_skills())}개 등록 완료")
    return registry


def load_agents(skills_registry: SkillsRegistry) -> dict:
    """모든 에이전트를 로드합니다."""
    agents = {}
    
    for agent_key, folder_name in AGENT_FOLDERS.items():
        agent_dir = os.path.join(AGENTS_DIR, folder_name)
        config_path = os.path.join(agent_dir, "config.json")
        instructions_path = os.path.join(agent_dir, "instructions.md")
        
        if os.path.exists(config_path) and os.path.exists(instructions_path):
            try:
                agent = AIAgent(config_path, instructions_path, skills_registry)
                agents[agent_key] = agent
                emoji = AGENT_EMOJI.get(agent_key, "🤖")
                print(f"  {emoji} {agent.name} 에이전트 로드 완료")
            except Exception as e:
                print(f"  ⚠️ {folder_name} 에이전트 로드 실패: {e}")
        else:
            print(f"  ⚠️ {folder_name} 설정 파일 없음, 건너뜀")
    
    return agents


def print_banner():
    """시작 배너를 출력합니다."""
    banner = """
╔══════════════════════════════════════════════════════╗
║                                                      ║
║     🧠  AI 에이전트 팀 시스템  v1.0                  ║
║                                                      ║
║     아이디어를 입력하면 팀이 실현합니다              ║
║                                                      ║
║     PM → Planner → Architect → Coder                ║
║                     → Reviewer → Tester              ║
║                                                      ║
╚══════════════════════════════════════════════════════╝
"""
    print(banner)


def main():
    """메인 함수 — 시스템을 초기화하고 실행합니다."""
    print_banner()
    
    # 1. 초기화
    print("🔧 시스템 초기화 중...")
    print("─" * 40)
    
    # 스킬 등록
    skills_registry = setup_skills()
    
    # 에이전트 로드
    print()
    print("🤖 에이전트 팀 로드 중...")
    print("─" * 40)
    agents = load_agents(skills_registry)
    
    if not agents:
        print("\n❌ 로드된 에이전트가 없습니다. 에이전트 설정을 확인해주세요.")
        return
    
    print(f"\n✅ 총 {len(agents)}개 에이전트 준비 완료\n")
    
    # 2. 오케스트레이터 생성
    config = {
        "DEFAULT_PIPELINE": DEFAULT_PIPELINE,
        "UI_PIPELINE": UI_PIPELINE,
        "MAX_FEEDBACK_LOOPS": MAX_FEEDBACK_LOOPS,
        "CONTEXT_DIR": CONTEXT_DIR,
        "OUTPUT_DIR": OUTPUT_DIR,
    }
    orchestrator = Orchestrator(agents, skills_registry, config)
    
    # 3. 사용자 입력 처리
    # 커맨드라인 인자가 있으면 직접 실행
    if len(sys.argv) > 1:
        user_idea = " ".join(sys.argv[1:])
        print(f"📥 입력된 아이디어: {user_idea}")
        orchestrator.run(user_idea)
        return
    
    # 대화형 모드
    print("=" * 50)
    print("💡 아이디어를 입력해주세요 (종료: 'q' 또는 'quit')")
    print("=" * 50)
    
    while True:
        try:
            user_idea = input("\n🎯 아이디어 > ").strip()
            
            if not user_idea:
                print("  ⚠️ 아이디어를 입력해주세요.")
                continue
            
            if user_idea.lower() in ('q', 'quit', 'exit', '종료'):
                print("\n👋 AI 에이전트 팀 시스템을 종료합니다. 감사합니다!")
                break
            
            # 파이프라인 실행
            orchestrator.run(user_idea)
            
            # 다음 프로젝트를 위해 새 오케스트레이터 생성
            orchestrator = Orchestrator(agents, skills_registry, config)
            
        except KeyboardInterrupt:
            print("\n\n👋 종료합니다.")
            break
        except Exception as e:
            print(f"\n❌ 오류 발생: {e}")
            import traceback
            traceback.print_exc()


if __name__ == "__main__":
    main()
