"""
오케스트레이터 — PM 에이전트의 두뇌
사용자의 아이디어를 전달받으면, 파이프라인에 정의된 순서대로
에이전트를 호출하고, 피드백 루프를 관리합니다.
"""
import os
import sys
from datetime import datetime
from typing import Dict, Optional, List

from .agent_runner import AIAgent, SkillsRegistry
from .message_bus import Message, MessageBus
from .context_manager import ProjectContext

sys.stdout.reconfigure(encoding='utf-8')


class Orchestrator:
    """
    전체 에이전트 팀을 오케스트레이션하는 PM 역할.
    
    워크플로우:
    1. 사용자 아이디어 수신
    2. PM이 파이프라인 결정 (UI 유무에 따라)
    3. 파이프라인 순서대로 에이전트 호출
    4. 에이전트 결과를 컨텍스트에 누적
    5. Reviewer/Tester 반려 시 피드백 루프 실행
    6. 최종 보고서 생성
    """

    def __init__(self, agents: Dict[str, AIAgent], skills_registry: SkillsRegistry, config: dict):
        """
        Args:
            agents: 에이전트 이름 → AIAgent 인스턴스 딕셔너리
            skills_registry: 공유 스킬 레지스트리
            config: 전역 설정 (config.py의 값들)
        """
        self.agents = agents
        self.skills = skills_registry
        self.config = config
        self.message_bus = MessageBus()
        self.context = None

    def run(self, user_idea: str) -> str:
        """
        전체 파이프라인을 실행합니다.
        
        Args:
            user_idea: 사용자의 아이디어 원문
            
        Returns:
            최종 보고서 문자열
        """
        print("\n" + "🚀" * 25)
        print("  AI 에이전트 팀 시스템 가동")
        print("🚀" * 25)
        print(f"\n💡 아이디어: {user_idea}\n")

        # 1. 프로젝트 컨텍스트 초기화
        self.context = ProjectContext(
            project_name=self._make_safe_name(user_idea[:30])
        )
        self.context.set_idea(user_idea)

        # 2. PM 에이전트로 파이프라인 결정
        pipeline = self._determine_pipeline(user_idea)
        self.context.metadata["pipeline_used"] = pipeline
        print(f"\n📋 파이프라인: {' → '.join(pipeline)}\n")

        # 3. PM 에이전트 실행 (분석)
        if "pm" in self.agents:
            pm_result = self.agents["pm"].run(user_idea)
            self.message_bus.send(Message(
                sender="pm", receiver="planner",
                content=pm_result, msg_type="request",
                context={"idea": user_idea}
            ))

        # 4. 파이프라인 순차 실행
        for step in pipeline:
            self.context.update_status("in_progress", step)
            agent = self.agents.get(step)
            
            if not agent:
                print(f"  ⚠️ '{step}' 에이전트를 찾을 수 없어 건너뜁니다.")
                continue

            # 현재 에이전트에 맞는 컨텍스트 준비
            agent_context = self.context.get_context_for(step)
            
            # 에이전트 실행
            result = agent.run(user_idea, context=agent_context)

            # 결과를 컨텍스트에 저장
            artifact_key = self._step_to_artifact(step)
            self.context.store_artifact(artifact_key, result)

            # 메시지 버스에 기록
            next_step = self._get_next_step(pipeline, step)
            self.message_bus.send(Message(
                sender=step,
                receiver=next_step or "pm",
                content=result,
                msg_type="result",
                context=agent_context
            ))

            # Reviewer 반려 처리
            if step == "reviewer" and "REJECTED" in result.upper():
                loops = self.context.increment_feedback_loops()
                max_loops = self.config.get("MAX_FEEDBACK_LOOPS", 3)
                
                if loops < max_loops:
                    print(f"\n🔄 피드백 루프 {loops}/{max_loops}: Coder에게 수정 요청")
                    self.message_bus.send(Message(
                        sender="reviewer", receiver="coder",
                        content=result, msg_type="feedback"
                    ))
                    # Coder 재실행
                    coder = self.agents.get("coder")
                    if coder:
                        revised_code = coder.run(user_idea, context={
                            **self.context.get_context_for("coder"),
                            "review_feedback": result
                        })
                        self.context.store_artifact("code", revised_code)
                else:
                    print(f"\n⚠️ 최대 피드백 루프({max_loops}회) 도달. 현재 상태로 진행합니다.")

            # Tester 실패 처리
            if step == "tester" and "FAILED" in result.upper():
                loops = self.context.increment_feedback_loops()
                max_loops = self.config.get("MAX_FEEDBACK_LOOPS", 3)
                
                if loops < max_loops:
                    print(f"\n🔄 피드백 루프 {loops}/{max_loops}: 테스트 실패 → Coder에게 수정 요청")
                    self.message_bus.send(Message(
                        sender="tester", receiver="coder",
                        content=result, msg_type="feedback"
                    ))

        # 5. 최종 보고서 생성
        final_report = self._generate_final_report(user_idea)
        self.context.store_artifact("final_report", final_report)
        self.context.update_status("completed")

        # 6. 산출물 저장
        context_dir = self.config.get("CONTEXT_DIR", "shared/context")
        saved_path = self.context.save_to_file(context_dir)
        
        # 메시지 히스토리 저장
        history_path = os.path.join(context_dir, f"{self.context.project_name}_messages.json")
        self.message_bus.save_history(history_path)

        # 7. 타임라인 출력
        self.message_bus.print_timeline()

        print(final_report)
        return final_report

    def _determine_pipeline(self, user_idea: str) -> List[str]:
        """사용자 아이디어를 분석하여 적절한 파이프라인을 결정합니다."""
        ui_keywords = ["웹", "앱", "UI", "화면", "페이지", "프론트엔드", 
                        "디자인", "인터페이스", "사이트", "홈페이지", "대시보드"]
        has_ui = any(keyword in user_idea for keyword in ui_keywords)
        
        if has_ui:
            return self.config.get("UI_PIPELINE", 
                                   ["planner", "architect", "designer", "coder", "reviewer", "tester"])
        else:
            return self.config.get("DEFAULT_PIPELINE", 
                                   ["planner", "architect", "coder", "reviewer", "tester"])

    def _step_to_artifact(self, step: str) -> str:
        """파이프라인 단계명을 산출물 키로 매핑합니다."""
        mapping = {
            "planner":   "prd",
            "architect": "architecture",
            "designer":  "ui_design",
            "coder":     "code",
            "reviewer":  "review",
            "tester":    "test_result",
        }
        return mapping.get(step, step)

    def _get_next_step(self, pipeline: List[str], current: str) -> Optional[str]:
        """파이프라인에서 다음 단계를 반환합니다."""
        try:
            idx = pipeline.index(current)
            if idx + 1 < len(pipeline):
                return pipeline[idx + 1]
        except ValueError:
            pass
        return None

    def _generate_final_report(self, user_idea: str) -> str:
        """최종 보고서를 생성합니다."""
        report = f"""
{'='*60}
🏁 최종 보고서 — AI 에이전트 팀
{'='*60}

📌 프로젝트: {self.context.project_name}
💡 아이디어: {user_idea}
📅 생성 시각: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
🔄 파이프라인: {' → '.join(self.context.metadata['pipeline_used'])}
📊 피드백 루프: {self.context.metadata['feedback_loops']}회
✅ 상태: 완료

{'─'*60}
📦 산출물 요약:
{'─'*60}"""

        artifact_names = {
            "prd": "📝 기획서 (PRD)",
            "architecture": "🏗️ 설계서",
            "ui_design": "🎨 UI 설계",
            "code": "💻 코드",
            "review": "🔍 리뷰 결과",
            "test_result": "🧪 테스트 결과",
        }

        for key, label in artifact_names.items():
            content = self.context.get_artifact(key)
            if content:
                report += f"\n  {label}: ✅ 완료 ({len(content)}자)"
            else:
                report += f"\n  {label}: ⬜ 생략"

        report += f"""

{'─'*60}
💾 산출물이 shared/context/ 디렉토리에 저장되었습니다.
{'='*60}
"""
        return report

    @staticmethod
    def _make_safe_name(text: str) -> str:
        """텍스트를 파일명에 안전한 형태로 변환합니다."""
        safe = "".join(c for c in text if c.isalnum() or c in " _-")
        return safe.strip().replace(" ", "_") if safe.strip() else "project"
