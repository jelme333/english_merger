def get_api_key():
    print("\n" + "="*50)
    print("=== OpenAI(GPT) API 연결 셋업 ===")
    print("="*50)
    print("충전이 완료된 OpenAI API 키(sk-...)를 아래에 붙여넣고 엔터를 치세요.")
    return input("API 키 입력: ").strip()

def display_progress(current, total, expression, status):
    # 진행 상황을 터미널에 보기 좋게 출력합니다.
    print(f"[{current}/{total}] '{expression}' 처리 중... 👉 {status}")

def print_message(msg):
    print(msg)