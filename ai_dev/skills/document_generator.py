"""
문서 생성 스킬 — PRD/설계서 등 문서 템플릿 기반 자동 생성
Planner, Architect 에이전트가 산출물을 작성할 때 사용합니다.
"""
import os


def generate_prd(idea: str) -> str:
    """
    [Skill] 아이디어를 기반으로 PRD(Product Requirements Document)를 생성합니다.
    
    시뮬레이션 모드에서는 템플릿 기반으로 생성하며,
    LLM 연동 시 AI가 실제 분석하여 내용을 채웁니다.
    
    Args:
        idea: 사용자의 원본 아이디어
        
    Returns:
        PRD 문서 문자열
    """
    prd = f"""# 📝 PRD (Product Requirements Document)

## 1. 프로젝트 개요
- **아이디어**: {idea}
- **작성일**: (자동 생성)
- **상태**: Draft

## 2. 5W1H 분석

| 항목 | 내용 |
|------|------|
| **Who (누가)** | 이 프로젝트의 주요 사용자/대상 |
| **What (무엇을)** | {idea} |
| **Why (왜)** | 이 프로젝트가 필요한 이유와 해결하려는 문제 |
| **When (언제)** | 예상 개발 기간 및 마일스톤 |
| **Where (어디서)** | 실행/배포 환경 (웹, 데스크톱, 모바일 등) |
| **How (어떻게)** | 기술적 접근 방식 및 핵심 구현 방법 |

## 3. 핵심 기능 목록 (Feature List)

### MVP (최소 실행 가능 제품)
| 우선순위 | 기능 | 설명 |
|----------|------|------|
| P0 (필수) | 핵심 기능 1 | 아이디어의 가장 기본적인 기능 |
| P0 (필수) | 핵심 기능 2 | 사용자 경험의 핵심 로직 |
| P1 (중요) | 부가 기능 1 | MVP에 포함되면 좋은 기능 |

### 향후 확장
| 우선순위 | 기능 | 설명 |
|----------|------|------|
| P2 (선택) | 확장 기능 1 | 차기 버전에서 고려 |
| P2 (선택) | 확장 기능 2 | 사용자 피드백 후 결정 |

## 4. 사용자 시나리오

### 시나리오 1: 기본 흐름
1. 사용자가 시스템에 접근한다
2. 핵심 기능을 수행한다
3. 결과를 확인한다

### 시나리오 2: 예외 흐름
1. 잘못된 입력이 들어온 경우
2. 시스템이 적절한 에러 메시지를 표시한다

## 5. 기술적 제약사항
- **언어/프레임워크**: Python 기반
- **실행 환경**: Windows
- **외부 의존성**: 최소화
- **성능 요구사항**: 응답 시간 3초 이내

## 6. 리스크 및 미결정 항목
- [ ] 상세 기능 범위 확정 필요
- [ ] 사용자 피드백 반영 필요

---
⚠️ 시뮬레이션 모드: LLM 연동 시 아이디어를 실제 분석하여 각 항목을 구체적으로 채웁니다.
"""
    return prd


def generate_design_doc(idea: str, prd: str = "") -> str:
    """
    [Skill] PRD를 기반으로 기술 설계서를 생성합니다.
    
    Args:
        idea: 원본 아이디어
        prd: PRD 문서 (Planner의 산출물)
        
    Returns:
        설계 문서 문자열
    """
    design_doc = f"""# 🏗️ 기술 설계서 (Architecture Design Document)

## 1. 프로젝트 개요
- **프로젝트**: {idea[:60]}
- **기반 문서**: PRD {'(참조됨)' if prd else '(미제공)'}

## 2. 시스템 아키텍처

### 2.1 아키텍처 패턴
- **레이어드 아키텍처** (Layered Architecture) 채택
- Presentation → Service → Repository → Data 4계층 구조

### 2.2 구조 다이어그램
```
┌─────────────────────────────────┐
│       Presentation Layer        │
│   (Routes / Controllers / UI)   │
├─────────────────────────────────┤
│        Service Layer            │
│   (Business Logic / Use Cases)  │
├─────────────────────────────────┤
│       Repository Layer          │
│   (Data Access / Persistence)   │
├─────────────────────────────────┤
│         Data Layer              │
│   (Database / External APIs)    │
└─────────────────────────────────┘
```

## 3. 데이터 모델

### 3.1 핵심 엔티티
```python
# 예시 데이터 모델 (프로젝트에 맞게 확장)
class BaseModel:
    id: int
    created_at: datetime
    updated_at: datetime
```

## 4. 폴더 구조
```
project/
├── main.py              # 진입점
├── config.py            # 설정 파일
├── models/              # 데이터 모델
│   └── __init__.py
├── services/            # 비즈니스 로직
│   └── __init__.py
├── repositories/        # 데이터 접근 계층
│   └── __init__.py
├── routes/              # API 엔드포인트 / UI 라우트
│   └── __init__.py
├── utils/               # 유틸리티 함수
│   └── __init__.py
└── tests/               # 테스트
    ├── test_models.py
    ├── test_services.py
    └── test_routes.py
```

## 5. 기술 스택
| 분류 | 기술 | 사유 |
|------|------|------|
| 언어 | Python 3.10+ | 기존 환경 호환 |
| 프레임워크 | (프로젝트에 따라 결정) | - |
| 테스트 | pytest | 표준 테스트 도구 |
| 린팅 | ruff / flake8 | 코드 품질 관리 |

## 6. API 설계 (해당 시)
| Method | Endpoint | 설명 |
|--------|----------|------|
| GET    | /api/v1/items | 목록 조회 |
| POST   | /api/v1/items | 새 항목 생성 |
| PUT    | /api/v1/items/:id | 항목 수정 |
| DELETE | /api/v1/items/:id | 항목 삭제 |

## 7. 설계 결정 (Trade-offs)
| 결정 | 대안 | 채택 이유 |
|------|------|-----------|
| 레이어드 아키텍처 | 마이크로서비스 | 초기 개발 속도, 단순성 |
| SQLite (기본) | PostgreSQL | 외부 의존성 최소화 |

---
⚠️ 시뮬레이션 모드: LLM 연동 시 PRD를 실제 분석하여 프로젝트에 맞는 설계서를 생성합니다.
"""
    return design_doc
