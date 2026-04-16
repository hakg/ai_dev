"""
컨텍스트 매니저 — 프로젝트 전체 컨텍스트를 관리
각 에이전트가 생산한 산출물(PRD, 설계서, 코드, 리뷰 등)을
누적 저장하고, 다음 에이전트에게 필요한 컨텍스트를 전달합니다.
"""
import os
import json
from datetime import datetime


class ProjectContext:
    """
    프로젝트 전체의 공유 컨텍스트.
    
    에이전트 파이프라인에서 각 단계의 산출물을 저장하고,
    다음 단계 에이전트에게 필요한 정보를 조합하여 전달합니다.
    
    Attributes:
        project_name: 프로젝트 이름
        user_idea: 사용자의 원본 아이디어
        artifacts: 단계별 산출물 딕셔너리
        metadata: 프로젝트 메타데이터
    """

    def __init__(self, project_name: str = "unnamed_project"):
        self.project_name = project_name
        self.user_idea = ""
        self.created_at = datetime.now().isoformat()
        
        # 단계별 산출물 저장소
        self.artifacts = {
            "idea":          "",   # 사용자 원본 아이디어
            "prd":           "",   # 기획서 (Planner 산출)
            "architecture":  "",   # 설계서 (Architect 산출)
            "ui_design":     "",   # UI 설계서 (Designer 산출)
            "code":          "",   # 구현 코드 (Coder 산출)
            "review":        "",   # 리뷰 결과 (Reviewer 산출)
            "test_result":   "",   # 테스트 결과 (Tester 산출)
            "final_report":  "",   # 최종 보고서 (PM 산출)
        }
        
        # 메타데이터
        self.metadata = {
            "pipeline_used":    [],
            "feedback_loops":   0,
            "status":           "initialized",  # initialized | in_progress | completed | failed
            "current_agent":    "",
        }

    def set_idea(self, idea: str) -> None:
        """사용자의 원본 아이디어를 저장합니다."""
        self.user_idea = idea
        self.artifacts["idea"] = idea
        self.metadata["status"] = "in_progress"

    def store_artifact(self, stage: str, content: str) -> None:
        """특정 단계의 산출물을 저장합니다."""
        if stage in self.artifacts:
            self.artifacts[stage] = content
        else:
            self.artifacts[stage] = content

    def get_artifact(self, stage: str) -> str:
        """특정 단계의 산출물을 반환합니다."""
        return self.artifacts.get(stage, "")

    def get_context_for(self, agent_type: str) -> dict:
        """
        특정 에이전트에게 필요한 컨텍스트를 조합하여 반환합니다.
        각 에이전트는 자신의 작업에 필요한 이전 단계 산출물만 받습니다.
        """
        context_map = {
            "planner":   {"idea": self.artifacts["idea"]},
            "architect": {"idea": self.artifacts["idea"],
                          "prd": self.artifacts["prd"]},
            "designer":  {"idea": self.artifacts["idea"],
                          "prd": self.artifacts["prd"],
                          "architecture": self.artifacts["architecture"]},
            "coder":     {"idea": self.artifacts["idea"],
                          "prd": self.artifacts["prd"],
                          "architecture": self.artifacts["architecture"],
                          "ui_design": self.artifacts["ui_design"]},
            "reviewer":  {"prd": self.artifacts["prd"],
                          "architecture": self.artifacts["architecture"],
                          "code": self.artifacts["code"]},
            "tester":    {"prd": self.artifacts["prd"],
                          "code": self.artifacts["code"],
                          "review": self.artifacts["review"]},
        }
        return context_map.get(agent_type, {"idea": self.artifacts["idea"]})

    def update_status(self, status: str, current_agent: str = "") -> None:
        """프로젝트 상태를 업데이트합니다."""
        self.metadata["status"] = status
        if current_agent:
            self.metadata["current_agent"] = current_agent

    def increment_feedback_loops(self) -> int:
        """피드백 루프 카운터를 증가시키고 현재 값을 반환합니다."""
        self.metadata["feedback_loops"] += 1
        return self.metadata["feedback_loops"]

    def save_to_file(self, context_dir: str) -> str:
        """
        전체 컨텍스트를 JSON 파일로 저장합니다.
        
        Returns:
            저장된 파일 경로
        """
        os.makedirs(context_dir, exist_ok=True)
        file_path = os.path.join(context_dir, f"{self.project_name}_context.json")
        data = {
            "project_name": self.project_name,
            "user_idea": self.user_idea,
            "created_at": self.created_at,
            "saved_at": datetime.now().isoformat(),
            "artifacts": self.artifacts,
            "metadata": self.metadata,
        }
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return file_path

    def generate_summary(self) -> str:
        """현재 프로젝트 컨텍스트의 요약을 문자열로 반환합니다."""
        lines = [
            f"📁 프로젝트: {self.project_name}",
            f"💡 아이디어: {self.user_idea[:80]}..." if len(self.user_idea) > 80 else f"💡 아이디어: {self.user_idea}",
            f"📊 상태: {self.metadata['status']}",
            f"🔄 피드백 루프: {self.metadata['feedback_loops']}회",
            f"🤖 현재 에이전트: {self.metadata['current_agent']}",
            "",
            "📦 산출물 현황:"
        ]
        for stage, content in self.artifacts.items():
            status = "✅ 완료" if content else "⬜ 대기"
            lines.append(f"  - {stage}: {status}")
        return "\n".join(lines)
