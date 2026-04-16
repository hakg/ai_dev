"""
메시지 버스 — 에이전트 간 메시지 전달 및 히스토리 관리
각 에이전트가 주고받는 메시지를 표준화된 형식으로 관리하여
컨텍스트 추적과 디버깅을 용이하게 합니다.
"""
import sys
import json
from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import Any, Optional, List

sys.stdout.reconfigure(encoding='utf-8')


@dataclass
class Message:
    """
    에이전트 간 전달되는 메시지의 표준 형식.
    
    Attributes:
        sender: 메시지를 보내는 에이전트 이름 (예: "planner", "coder")
        receiver: 메시지를 받는 에이전트 이름
        content: 메시지 본문 (작업 결과, 요청 내용 등)
        msg_type: 메시지 유형 ("request", "result", "feedback", "error")
        context: 이전 단계에서 누적된 컨텍스트 데이터
        timestamp: 메시지 생성 시각
    """
    sender: str
    receiver: str
    content: str
    msg_type: str = "result"       # request | result | feedback | error
    context: dict = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> dict:
        return asdict(self)

    def summary(self) -> str:
        """메시지 요약 출력 (디버깅용)"""
        preview = self.content[:80] + "..." if len(self.content) > 80 else self.content
        return f"[{self.msg_type.upper()}] {self.sender} → {self.receiver}: {preview}"


class MessageBus:
    """
    에이전트 간 메시지를 중계하고 전체 히스토리를 관리하는 버스.
    
    주요 기능:
    - 메시지 전송 (send)
    - 특정 에이전트의 수신 메시지 조회 (get_messages_for)
    - 전체 히스토리 조회 (get_history)
    - 히스토리 파일 저장 (save_history)
    """

    def __init__(self):
        self._history: List[Message] = []

    def send(self, message: Message) -> None:
        """메시지를 버스에 등록하고 콘솔에 로그를 출력합니다."""
        self._history.append(message)
        print(f"  📨 {message.summary()}")

    def get_messages_for(self, receiver: str) -> List[Message]:
        """특정 에이전트가 수신한 모든 메시지를 반환합니다."""
        return [m for m in self._history if m.receiver == receiver]

    def get_latest_for(self, receiver: str) -> Optional[Message]:
        """특정 에이전트가 받은 가장 최근 메시지를 반환합니다."""
        messages = self.get_messages_for(receiver)
        return messages[-1] if messages else None

    def get_messages_from(self, sender: str) -> List[Message]:
        """특정 에이전트가 보낸 모든 메시지를 반환합니다."""
        return [m for m in self._history if m.sender == sender]

    def get_latest_from(self, sender: str) -> Optional[Message]:
        """특정 에이전트가 보낸 가장 최근 메시지를 반환합니다."""
        messages = self.get_messages_from(sender)
        return messages[-1] if messages else None

    def get_history(self) -> List[Message]:
        """전체 메시지 히스토리를 반환합니다."""
        return list(self._history)

    def save_history(self, file_path: str) -> None:
        """메시지 히스토리를 JSON 파일로 저장합니다."""
        import os
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        data = [m.to_dict() for m in self._history]
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"  💾 메시지 히스토리 저장 완료: {file_path}")

    def clear(self) -> None:
        """히스토리를 초기화합니다."""
        self._history.clear()

    def print_timeline(self) -> None:
        """전체 메시지 타임라인을 보기 좋게 출력합니다."""
        print("\n" + "=" * 60)
        print("📋 메시지 타임라인")
        print("=" * 60)
        for i, msg in enumerate(self._history, 1):
            icon = {"request": "📩", "result": "✅", "feedback": "🔄", "error": "❌"}.get(msg.msg_type, "📨")
            print(f"  {i}. {icon} [{msg.timestamp[11:19]}] {msg.sender} → {msg.receiver}")
            preview = msg.content[:100] + "..." if len(msg.content) > 100 else msg.content
            print(f"     {preview}")
        print("=" * 60 + "\n")
