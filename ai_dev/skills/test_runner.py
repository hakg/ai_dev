"""
테스트 러너 스킬 — 테스트 실행 및 결과 리포트 도구
Tester 에이전트가 코드 검증을 수행할 때 사용합니다.
"""
import subprocess
import os


def run_tests(test_dir: str = "tests", verbose: bool = True) -> str:
    """
    [Skill] pytest를 사용하여 테스트를 실행합니다.
    
    Args:
        test_dir: 테스트 파일이 있는 디렉토리
        verbose: 상세 출력 여부
        
    Returns:
        테스트 실행 결과 문자열
    """
    try:
        cmd = ["python", "-m", "pytest", test_dir]
        if verbose:
            cmd.append("-v")
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=60,
            encoding='utf-8'
        )
        
        output = result.stdout + result.stderr
        
        if result.returncode == 0:
            return f"[Success] 모든 테스트 통과\n{output}"
        else:
            return f"[Failed] 일부 테스트 실패 (exit code: {result.returncode})\n{output}"
            
    except FileNotFoundError:
        return "[Error] pytest가 설치되어 있지 않습니다. 'pip install pytest'로 설치해주세요."
    except subprocess.TimeoutExpired:
        return "[Error] 테스트 실행 시간 초과 (60초)"
    except Exception as e:
        return f"[Error] 테스트 실행 실패: {str(e)}"


def generate_test_report(test_results: str) -> str:
    """
    [Skill] 테스트 결과를 보기 좋은 리포트로 변환합니다.
    
    Args:
        test_results: 테스트 실행 결과 문자열
        
    Returns:
        포맷된 테스트 리포트
    """
    # 결과 파싱
    passed = test_results.count("PASSED")
    failed = test_results.count("FAILED")
    errors = test_results.count("ERROR")
    total = passed + failed + errors

    # 전체 통과율 계산
    pass_rate = (passed / total * 100) if total > 0 else 0

    report = f"""
🧪 테스트 리포트
{'━' * 40}
📊 결과 요약:
  ✅ 통과: {passed}건
  ❌ 실패: {failed}건
  ⚠️ 에러: {errors}건
  📈 통과율: {pass_rate:.1f}%

📋 상세 결과:
{test_results}
{'━' * 40}
"""
    return report
