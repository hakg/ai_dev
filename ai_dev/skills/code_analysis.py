"""
코드 분석 스킬 — Python 코드 정적 분석 도구
Reviewer 에이전트가 코드 품질을 검증할 때 사용합니다.
"""
import ast
import re


def analyze_code(code: str) -> str:
    """
    [Skill] Python 코드를 정적 분석하여 결과를 반환합니다.
    구문 검증, 함수/클래스 수, 잠재적 이슈 등을 검사합니다.
    
    Args:
        code: 분석할 Python 코드 문자열
        
    Returns:
        분석 결과 문자열
    """
    results = []
    
    # 1. 구문 검증
    try:
        tree = ast.parse(code)
        results.append("  ✅ 구문 검증: 정상 (문법 오류 없음)")
    except SyntaxError as e:
        results.append(f"  ❌ 구문 오류: {e.msg} (라인 {e.lineno})")
        return "\n".join(results)

    # 2. 구조 분석
    classes = [node for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]
    functions = [node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]
    imports = [node for node in ast.walk(tree) if isinstance(node, (ast.Import, ast.ImportFrom))]
    
    results.append(f"  📊 구조: 클래스 {len(classes)}개, 함수 {len(functions)}개, import {len(imports)}개")

    # 3. 라인 수 분석
    lines = code.strip().split('\n')
    code_lines = [l for l in lines if l.strip() and not l.strip().startswith('#')]
    comment_lines = [l for l in lines if l.strip().startswith('#')]
    
    results.append(f"  📏 라인: 전체 {len(lines)}줄 (코드 {len(code_lines)}, 주석 {len(comment_lines)})")

    # 4. 잠재적 이슈 검사
    issues = []
    
    # 하드코딩된 비밀번호 검사
    password_patterns = [r'password\s*=\s*["\']', r'secret\s*=\s*["\']', r'api_key\s*=\s*["\']']
    for pattern in password_patterns:
        if re.search(pattern, code, re.IGNORECASE):
            issues.append("⚠️ 하드코딩된 비밀번호/키 발견")
            break
    
    # bare except 검사
    if 'except:' in code or 'except Exception:' in code:
        issues.append("💡 세부적인 예외 처리 고려 필요")
    
    # TODO 검사
    todos = re.findall(r'#\s*TODO', code, re.IGNORECASE)
    if todos:
        issues.append(f"📝 미완성 TODO {len(todos)}건 발견")

    if issues:
        results.append("  🔎 발견된 이슈:")
        for issue in issues:
            results.append(f"    - {issue}")
    else:
        results.append("  ✅ 잠재적 이슈: 발견 없음")

    return "\n".join(results)


def count_lines(code: str) -> dict:
    """
    [Skill] 코드의 라인 수를 분류하여 카운트합니다.
    
    Args:
        code: 분석할 코드 문자열
        
    Returns:
        라인 수 딕셔너리 (total, code, comment, blank)
    """
    lines = code.split('\n')
    total = len(lines)
    blank = sum(1 for l in lines if not l.strip())
    comment = sum(1 for l in lines if l.strip().startswith('#'))
    code_count = total - blank - comment
    
    return {
        "total": total,
        "code": code_count,
        "comment": comment,
        "blank": blank,
    }
