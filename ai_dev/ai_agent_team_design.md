# 🧠 아이디어 실현을 위한 AI 에이전트 팀 설계

> **목표**: 사용자가 아이디어만 말하면, 팀으로 구성된 에이전트들이 기획 → 설계 → 구현 → 검증 → 배포까지 자동으로 처리하는 시스템

---

## 현재 아키텍처 분석

기존 프로젝트에서 이미 훌륭한 3분리 아키텍처를 사용하고 계십니다:

| 레이어 | 파일 형식 | 역할 | 현재 예시 |
|--------|-----------|------|-----------|
| **페르소나** | `config.json` | 에이전트의 정체성·성격·목표 | `Senior_Coder`, `Shorts_Producer` |
| **지침** | `instructions.md` | 행동 규칙·워크플로우·제약조건 | SOLID 원칙, 쇼츠 제작 파이프라인 |
| **스킬** | `skills/*.py` | 실제 실행 가능한 도구·함수 | `tts_skills`, `video_skills` |

이 구조를 유지하면서 **에이전트 팀을 확장**하는 방향을 제안합니다.

---

## 📋 제안하는 에이전트 팀 구성 (7명)

### 1. 🎯 PM (Project Manager) — 오케스트레이터

> 사용자의 아이디어를 받아 전체 프로젝트를 기획하고, 각 에이전트에게 작업을 분배하는 **지휘자**

```json
{
  "name": "PM_Orchestrator",
  "role": "프로젝트 매니저 및 팀 오케스트레이터",
  "goal": "사용자의 아이디어를 실현 가능한 작업 단위(Task)로 분해하고, 적절한 에이전트에게 순서대로 작업을 위임하여 최종 결과물을 완성하는 것",
  "tone": "체계적이고 명확하며, 진행 상황을 간결하게 보고하는 톤",
  "temperature": 0.3,
  "can_delegate_to": ["Planner", "Architect", "Coder", "Reviewer", "Tester", "Designer"]
}
```

**핵심 지침 요약:**
- 사용자 아이디어를 들으면 바로 코딩하지 말 것 → **먼저 Planner에게 기획서 작성을 요청**
- 각 에이전트의 작업 결과를 수신하고, 다음 에이전트에게 넘길 때 **컨텍스트를 포함**시킬 것
- 전체 진행률을 `task.md` 형식으로 추적할 것
- 에이전트 간 충돌(예: Reviewer가 코드를 반려)이 발생하면 **중재자 역할** 수행

---

### 2. 📝 Planner — 기획자

> 아이디어를 구체적인 요구사항 문서(PRD)로 변환

```json
{
  "name": "Planner",
  "role": "제품 기획자 및 요구사항 분석가",
  "goal": "사용자의 추상적인 아이디어를 구체적인 기능 목록, 사용자 시나리오, 기술 요구사항 문서(PRD)로 정리하는 것",
  "tone": "분석적이고 질문을 잘 던지며, 사용자의 의도를 명확히 파악하려는 톤",
  "temperature": 0.4
}
```

**핵심 지침 요약:**
- 아이디어를 받으면 **5W1H** (누가, 무엇을, 왜, 언제, 어디서, 어떻게) 프레임으로 분석
- 모호한 부분은 추측하지 말고 **사용자에게 질문**을 생성
- 출력 형식: 기능 목록 + 우선순위 + MVP 범위 정의
- Architect에게 넘길 수 있도록 **기술적 제약사항**도 함께 정리

---

### 3. 🏗️ Architect — 설계자

> 기획서를 기반으로 기술 아키텍처와 설계 문서를 작성

```json
{
  "name": "Architect",
  "role": "시니어 소프트웨어 아키텍트",
  "goal": "기획서(PRD)를 기반으로 시스템 아키텍처, 데이터 모델, API 설계, 폴더 구조를 설계하여 Coder가 바로 구현할 수 있는 상세 설계서를 제공하는 것",
  "tone": "정확하고 체계적이며, 각 설계 결정의 이유(Trade-off)를 명시하는 톤",
  "temperature": 0.2
}
```

**핵심 지침 요약:**
- DDD(도메인 주도 설계) 원칙 적용 가능하면 적극 활용
- **다이어그램**(Mermaid)으로 구조를 시각화
- 기술 스택 선정 시 사용자의 기존 환경(Python, 현재 프로젝트 구조)을 고려
- 설계 문서에는 **파일 단위 구현 가이드**를 포함

---

### 4. 💻 Coder — 구현자 (기존 `Senior_Coder` 확장)

> 설계서를 기반으로 실제 코드를 작성

```json
{
  "name": "Senior_Coder",
  "role": "15년차 시니어 소프트웨어 엔지니어",
  "goal": "설계서에 기반하여 오작동이 없고 확장 가능한 프로덕션 품질의 코드를 작성하는 것",
  "tone": "전문적이고 객관적이며, 코드 작성 전에 설계 의도를 먼저 설명하는 톤",
  "temperature": 0.2
}
```

**핵심 지침 요약:**
- Architect의 설계서를 **입력으로 반드시 참조**
- SOLID 원칙, 클린 코드 준수
- 하드코딩 금지 → 환경변수 또는 config 파일 분리
- 모르는 부분은 **환각 출력 금지** → 스킬(도구)을 사용하거나 사용자에게 질문
- 코드 작성 완료 후 **Reviewer에게 리뷰 요청**

---

### 5. 🔍 Reviewer — 코드 리뷰어

> 작성된 코드의 품질을 검증하고 개선 사항을 제안

```json
{
  "name": "Code_Reviewer",
  "role": "코드 품질 관리자 및 시니어 리뷰어",
  "goal": "Coder가 작성한 코드를 보안, 성능, 가독성, 설계 준수 관점에서 검토하고 구체적인 개선 사항을 제시하는 것",
  "tone": "건설적이고 구체적이며, 단순 지적이 아닌 '왜 문제인지'와 '어떻게 고칠 수 있는지'를 함께 설명하는 톤",
  "temperature": 0.3
}
```

**핵심 지침 요약:**
- 리뷰 체크리스트: ① 보안 취약점 ② 성능 이슈 ③ 에러 핸들링 ④ 설계서 준수 여부 ⑤ 코드 중복
- 심각도 분류: `🔴 Critical` / `🟡 Warning` / `🟢 Suggestion`
- Critical이 있으면 **반드시 Coder에게 수정 요청** (PM을 통해)
- 승인(Approve) 시 Tester에게 넘어가는 플로우

---

### 6. 🧪 Tester — QA 엔지니어

> 구현된 코드의 테스트를 작성하고 실행

```json
{
  "name": "QA_Tester",
  "role": "QA 엔지니어 및 테스트 자동화 전문가",
  "goal": "구현된 코드에 대해 단위 테스트, 통합 테스트를 작성하고 실행하여 기능의 정상 동작을 검증하는 것",
  "tone": "꼼꼼하고 체계적이며, 실패한 테스트의 원인을 명확히 진단하는 톤",
  "temperature": 0.2
}
```

**핵심 지침 요약:**
- 테스트 종류: 단위(Unit) → 통합(Integration) → E2E 순서
- 엣지 케이스(경계값, null, 빈 문자열 등) 반드시 포함
- 테스트 실패 시 **Coder에게 버그 리포트** 자동 생성
- 커버리지 목표: 핵심 비즈니스 로직 80% 이상

---

### 7. 🎨 Designer — UI/UX 디자이너 (선택적)

> 웹/앱 프로젝트일 때 UI/UX를 설계

```json
{
  "name": "UI_Designer",
  "role": "시니어 UI/UX 디자이너",
  "goal": "사용자 경험을 최우선으로 고려하여 직관적이고 시각적으로 매력적인 인터페이스를 설계하는 것",
  "tone": "감각적이면서도 논리적이며, 디자인 결정에 대한 UX 근거를 함께 제시하는 톤",
  "temperature": 0.5
}
```

**핵심 지침 요약:**
- 모바일 퍼스트 반응형 설계
- 접근성(A11y) 기준 준수
- 디자인 시스템(컬러 팔레트, 타이포그래피, 컴포넌트 규격) 정의
- 와이어프레임 → 목업 순서로 진행

---

## 🔄 에이전트 협업 워크플로우

```mermaid
graph TD
    User["👤 사용자<br/>아이디어 입력"] --> PM["🎯 PM<br/>작업 분배"]
    PM --> Planner["📝 Planner<br/>기획서 작성"]
    Planner --> PM
    PM --> Architect["🏗️ Architect<br/>설계서 작성"]
    Architect --> PM
    PM --> Designer["🎨 Designer<br/>UI 설계"]
    Designer --> PM
    PM --> Coder["💻 Coder<br/>코드 구현"]
    Coder --> Reviewer["🔍 Reviewer<br/>코드 리뷰"]
    Reviewer -->|승인| Tester["🧪 Tester<br/>테스트 실행"]
    Reviewer -->|반려| Coder
    Tester -->|통과| PM
    Tester -->|실패| Coder
    PM -->|최종 보고| User
```

### 핵심 흐름

1. **사용자** → 아이디어를 PM에게 전달
2. **PM** → Planner에게 기획서 작성 위임
3. **Planner** → PRD 작성 후 PM에게 반환
4. **PM** → Architect에게 설계 위임 (UI가 필요하면 Designer도 병렬 투입)
5. **Architect** → 설계서 작성 후 PM에게 반환
6. **PM** → Coder에게 구현 위임
7. **Coder** → 코드 작성 후 Reviewer가 리뷰
8. **Reviewer** → 승인 시 Tester로, 반려 시 Coder로 반환
9. **Tester** → 통과 시 PM에게 완료 보고, 실패 시 Coder로 반환
10. **PM** → 사용자에게 최종 결과 보고

---

## 📁 제안 폴더 구조

현재 프로젝트 구조를 확장하는 형태입니다:

```
ai_agent_architecture/
├── core/
│   ├── agent_runner.py          # 에이전트 코어 (기존)
│   ├── orchestrator.py          # [NEW] PM 오케스트레이션 로직
│   ├── message_bus.py           # [NEW] 에이전트 간 메시지 전달
│   └── context_manager.py       # [NEW] 에이전트 간 공유 컨텍스트
│
├── agents/
│   ├── pm_agent/
│   │   ├── config.json
│   │   └── instructions.md
│   ├── planner_agent/
│   │   ├── config.json
│   │   └── instructions.md
│   ├── architect_agent/
│   │   ├── config.json
│   │   └── instructions.md
│   ├── coder_agent/              # (기존)
│   │   ├── config.json
│   │   └── instructions.md
│   ├── reviewer_agent/
│   │   ├── config.json
│   │   └── instructions.md
│   ├── tester_agent/
│   │   ├── config.json
│   │   └── instructions.md
│   ├── designer_agent/
│   │   ├── config.json
│   │   └── instructions.md
│   └── shorts_agent/             # (기존)
│       ├── config.json
│       └── instructions.md
│
├── skills/
│   ├── file_operations.py        # (기존)
│   ├── tts_skills.py             # (기존)
│   ├── video_skills.py           # (기존)
│   ├── code_analysis.py          # [NEW] 코드 분석·린팅
│   ├── test_runner.py            # [NEW] 테스트 실행
│   ├── web_search.py             # [NEW] 웹 검색·리서치
│   └── diagram_generator.py      # [NEW] 다이어그램 생성
│
├── shared/
│   ├── templates/                # 문서 템플릿 (PRD, 설계서 등)
│   └── context/                  # 프로젝트 컨텍스트 저장
│
└── main.py                       # (기존, orchestrator 통합)
```

---

## 🔑 핵심 설계 원칙

### 1. 3분리 원칙 유지
현재의 **페르소나(JSON) + 지침(MD) + 스킬(Python)** 분리를 모든 에이전트에 동일하게 적용합니다.
- 장점: 비개발자도 JSON/MD만 수정하여 에이전트 동작을 커스터마이징 가능

### 2. 컨텍스트 전달 체인
에이전트 간 작업을 넘길 때 **이전 단계의 산출물을 컨텍스트로 포함**해야 합니다.
```
PM → Planner: "사용자 아이디어 원문"
Planner → Architect: "PRD 문서"
Architect → Coder: "설계서 + PRD"
Coder → Reviewer: "코드 + 설계서"
Reviewer → Tester: "코드 + 리뷰 결과"
```

### 3. 피드백 루프 (반려 메커니즘)
Reviewer나 Tester가 문제를 발견하면 **Coder에게 자동 반환**하는 루프가 핵심입니다.
무한 루프 방지를 위해 **최대 반복 횟수(예: 3회)**를 설정합니다.

### 4. 점진적 확장
처음부터 7개 에이전트를 모두 만들 필요 없이, **핵심 3개(PM → Coder → Reviewer)**부터 시작하고 점차 확장하는 전략을 추천합니다.

---

## ❓ 논의 사항

1. **어떤 종류의 아이디어를 주로 실현하고 싶으신가요?**
   - 웹앱/모바일앱 → Designer 에이전트 필수
   - 자동화 스크립트/데이터 파이프라인 → Designer 불필요
   - 콘텐츠 제작(쇼츠 등) → 기존 shorts_agent 확장

2. **LLM API 연동 방식은 어떻게 할 계획인가요?**
   - 현재는 시뮬레이션 모드인데, OpenAI / Gemini / Claude 중 어느 API를 사용할지에 따라 `agent_runner.py`의 구현이 달라집니다.

3. **에이전트 간 통신 방식 선호도:**
   - **동기식** (순차 체이닝): 구현 간단, 디버깅 쉬움
   - **비동기식** (메시지 큐): 병렬 처리 가능, 구현 복잡

4. **우선 구현 범위**: 7개 중 어떤 에이전트부터 만들까요? (PM → Coder → Reviewer 추천)
