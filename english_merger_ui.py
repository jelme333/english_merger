def get_api_key():
    print("\n" + "="*50)
    print("=== OpenAI(GPT) 기반 영어 표현 지능형 자동화 봇 ===")
    print("="*50)
    print("충전이 완료된 OpenAI API 키(sk-...)를 아래에 붙여넣고 엔터를 치세요.")
    return input("API 키 입력: ").strip()

def get_file_names():
    print("\n[작업 모드 설정]")
    print("💡 1개 파일만 입력하면 '빈칸 채우기'만 진행하고, 2개를 입력하면 '통합 후 채우기'를 진행합니다.")
    
    file1 = input("1. 기준 파일명 (기본값: 통합_영어표현모음.csv) [필수]: ").strip()
    if not file1: file1 = "통합_영어표현모음.csv"
        
    file2 = input("2. 합칠 파일명 (합칠 파일이 없으면 그냥 엔터를 치세요) [선택]: ").strip()
    
    return file1, file2

def display_progress(current, total, expression, status):
    print(f"[{current}/{total}] '{expression}' 처리 중... 👉 {status}")

def print_message(msg):
    print(msg)
