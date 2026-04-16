"""
파일 조작 스킬 — 파일 읽기/쓰기 도구
에이전트가 파일 시스템과 상호작용할 때 사용합니다.
"""
import os


def read_file(file_path: str) -> str:
    """
    [Skill] 파일의 내용을 읽어 반환합니다.
    에이전트가 컨텍스트 파악을 위해 파일을 읽을 때 호출합니다.
    
    Args:
        file_path: 읽을 파일의 경로
        
    Returns:
        파일 내용 문자열, 또는 에러 메시지
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return f"[Error] 파일을 찾을 수 없습니다: {file_path}"
    except Exception as e:
        return f"[Error] 파일 읽기 실패: {str(e)}"


def write_code(file_path: str, code: str) -> str:
    """
    [Skill] 코드를 파일로 저장합니다.
    에이전트가 코드를 완성한 후 디스크에 반영할 때 호출합니다.
    
    Args:
        file_path: 저장할 파일 경로
        code: 저장할 코드 내용
        
    Returns:
        성공/실패 메시지
    """
    try:
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(code)
        return f"[Success] {file_path} 파일이 성공적으로 저장되었습니다."
    except Exception as e:
        return f"[Error] 파일 저장 실패: {str(e)}"


def list_directory(dir_path: str) -> str:
    """
    [Skill] 디렉토리의 파일 목록을 반환합니다.
    
    Args:
        dir_path: 조회할 디렉토리 경로
        
    Returns:
        파일 목록 문자열
    """
    try:
        if not os.path.isdir(dir_path):
            return f"[Error] 디렉토리가 아닙니다: {dir_path}"
        
        items = []
        for item in sorted(os.listdir(dir_path)):
            full_path = os.path.join(dir_path, item)
            if os.path.isdir(full_path):
                items.append(f"  📁 {item}/")
            else:
                size = os.path.getsize(full_path)
                items.append(f"  📄 {item} ({size} bytes)")
        
        return f"📂 {dir_path}\n" + "\n".join(items) if items else f"📂 {dir_path} (비어있음)"
    except Exception as e:
        return f"[Error] 디렉토리 조회 실패: {str(e)}"
