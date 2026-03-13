import pandas as pd
import os
from english_merger_logic import clean_and_deduplicate, merge_expressions, process_with_openai
from english_merger_ui import get_api_key, get_file_names, display_progress, print_message

def smart_parse_dataframe(df):
    """2026-02-28 원칙: 헤더명 기준 유연한 스마트 파싱 적용"""
    df.columns = df.columns.str.strip()
    col_map = {}
    for col in df.columns:
        if '표현' in col or '단어' in col or '숙어' in col: col_map[col] = '표현'
        elif '뜻' in col or '의미' in col: col_map[col] = '뜻'
        elif '예문 1' in col: col_map[col] = '예문 1'
        elif '예문 2' in col: col_map[col] = '예문 2'
        elif '예문 3' in col: col_map[col] = '예문 3'
        elif '강조' in col or '포인트' in col: col_map[col] = '강조 포인트'
    
    df.rename(columns=col_map, inplace=True)
    
    # 필수 열이 없으면 에러가 나지 않도록 빈 열 자동 생성
    for req_col in ['표현', '뜻', '예문 1', '예문 2', '예문 3', '강조 포인트']:
        if req_col not in df.columns:
            df[req_col] = pd.NA
    return df

def main():
    # 1. API 키 및 파일명 입력 받기 (UI 호출)
    api_key = get_api_key()
    if not api_key:
        print_message("API 키가 입력되지 않아 작업을 종료합니다.")
        return
        
    file1_path, file2_path = get_file_names()

    if not os.path.exists(file1_path):
        print_message(f"\n❌ 에러: 기준 파일인 '{file1_path}'을(를) 찾을 수 없습니다.")
        return

    try:
        print_message(f"\n🔄 1. '{file1_path}' 읽기 및 스마트 파싱(양식 통일) 진행 중...")
        target_df = pd.read_csv(file1_path, encoding='utf-8-sig')
        target_df = smart_parse_dataframe(target_df)
        
        # 2. 파일2가 입력되었는지 확인 (하이브리드 분기점)
        if file2_path:
            if not os.path.exists(file2_path):
                print_message(f"\n❌ 에러: 합칠 파일인 '{file2_path}'을(를) 찾을 수 없습니다.")
                return
            
            print_message(f"🔄 2. '{file2_path}' 읽기 및 스마트 파싱 진행 중...")
            df2 = pd.read_csv(file2_path, encoding='utf-8-sig')
            df2 = smart_parse_dataframe(df2)
            
            print_message("🔄 3. 중복 단어 제거 및 두 파일 통합 중...")
            # (logic 파일의 기능을 쓰기 위해 임시로 정리된 열 생성)
            target_df['표현_clean'] = target_df['표현'].astype(str).str.lower().str.replace(" ", "")
            df2['표현_clean'] = df2['표현'].astype(str).str.lower().str.replace(" ", "")
            
            target_df = merge_expressions(target_df, df2)
            print_message(f"✅ 통합 완료! 총 {len(target_df)}개의 단어가 준비되었습니다.")
            output_prefix = "최종완성_통합본"
            
        else:
            print_message("✅ 두 번째 파일이 입력되지 않아 '단일 파일 빈칸 채우기' 모드로 진행합니다.")
            output_prefix = "최종완성_단일"

    except Exception as e:
        print_message(f"\n❌ 파일 처리 중 에러 발생: {e}")
        return

    # 4. 빈칸 채우기 (OpenAI 호출)
    print_message("\n🚀 빈칸(예문/강조 포인트) AI 생성을 시작합니다...")
    result_df = process_with_openai(target_df, api_key, display_progress)
    
    # 5. 불필요한 임시 열(표현_clean) 지우고 최종 저장
    if '표현_clean' in result_df.columns:
        result_df.drop(columns=['표현_clean'], inplace=True)
        
    output_filename = f"{output_prefix}.csv"
    result_df.to_csv(output_filename, index=False, encoding='utf-8-sig')
    
    print_message("\n" + "="*50)
    print_message(f"✅ 모든 작업이 완벽하게 끝났습니다!")
    print_message(f"✅ 폴더에 '{output_filename}' 파일이 새로 생성되었습니다.")
    print_message("="*50)

if __name__ == "__main__":
    main()
