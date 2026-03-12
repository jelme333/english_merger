import pandas as pd
import os
from english_merger_logic import clean_and_deduplicate, merge_expressions, process_with_openai
from english_merger_ui import get_api_key, display_progress, print_message

def main():
    # 1. 작업할 파일 이름 설정 (구글 시트에 올리셨던 바로 그 통합 파일입니다)
    file_path = "통합_영어표현_최종완성본.csv" 
    
    if not os.path.exists(file_path):
        print_message(f"\n❌ 에러: '{file_path}' 파일을 찾을 수 없습니다.")
        print_message("파이썬 코드가 있는 폴더(src) 안에 해당 CSV 파일이 있는지 확인해 주세요.")
        return

    try:
        # 파일 읽어오기 (스마트 파싱 적용을 위해 pandas 사용)
        df = pd.read_csv(file_path, encoding='utf-8-sig')
        
        # --- [스마트 파싱 적용] 헤더명 유연성 확보 ---
        # 1. 눈에 보이지 않는 앞뒤 공백(띄어쓰기) 완벽 제거
        df.columns = df.columns.str.strip()
        
        # 2. 컬럼명이 '영어 표현', '표현(단어)', '단어/숙어' 등 달라도 유연하게 '표현'으로 자동 통일
        col_map = {}
        for col in df.columns:
            if '표현' in col or '단어' in col or '숙어' in col: col_map[col] = '표현'
            elif '뜻' in col or '의미' in col: col_map[col] = '뜻'
            elif '예문 1' in col: col_map[col] = '예문 1'
            elif '예문 2' in col: col_map[col] = '예문 2'
            elif '예문 3' in col: col_map[col] = '예문 3'
            elif '강조' in col or '포인트' in col: col_map[col] = '강조 포인트'
        df.rename(columns=col_map, inplace=True)
        
        # 3. 만약 엑셀에 특정 예문 열이 아예 없다면 에러가 나지 않도록 자동으로 빈 열 생성
        for req_col in ['표현', '뜻', '예문 1', '예문 2', '예문 3', '강조 포인트']:
            if req_col not in df.columns:
                df[req_col] = pd.NA

    except Exception as e:
        print_message(f"\n❌ 파일 읽기 에러: {e}")
        return

    # 2. UI 모듈을 통해 사용자에게 API 키 입력받기
    api_key = get_api_key()
    if not api_key:
        print_message("API 키가 입력되지 않아 작업을 종료합니다.")
        return

    print_message("\n🚀 OpenAI(GPT-4o-mini) 서버를 통해 빈칸 채우기를 시작합니다...")
    print_message("💡 안내: 서버 차단(과부하)을 막기 위해 0.5초에 1개씩 안전하게 자동 처리됩니다. 커피 한 잔 드시고 오세요!\n")
    
    # 3. 로직 모듈의 GPT 처리 함수 호출
    result_df = process_with_openai(df, api_key, display_progress)
    
    # 4. 완료된 데이터를 새로운 파일로 저장
    output_filename = "최종완성_GPT_영어표현모음.csv"
    result_df.to_csv(output_filename, index=False, encoding='utf-8-sig')
    
    print_message("\n" + "="*50)
    print_message(f"✅ 모든 작업이 완벽하게 끝났습니다!")
    print_message(f"✅ 폴더에 '{output_filename}' 파일이 새로 생성되었습니다.")
    print_message("="*50)

if __name__ == "__main__":
    main()