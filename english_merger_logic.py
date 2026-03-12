import pandas as pd
from openai import OpenAI
import time

def clean_and_deduplicate(df, col_map):
    df.rename(columns=col_map, inplace=True)
    df['표현_clean'] = df['표현'].astype(str).str.strip().str.lower()
    return df.drop_duplicates(subset=['표현_clean'], keep='first')

def merge_expressions(df1, df2):
    df2_filtered = df2[~df2['표현_clean'].isin(df1['표현_clean'])]
    return pd.concat([df1, df2_filtered], ignore_index=True)

def process_with_openai(df, api_key, update_callback):
    client = OpenAI(api_key=api_key)
    
    for index, row in df.iterrows():
        missing = []
        if pd.isna(row['예문 1']): missing.append("예문 1 (일상 대화)")
        if pd.isna(row['예문 2']): missing.append("예문 2 (비즈니스 - HR, 경영지원, 영업 등)")
        if pd.isna(row['예문 3']): missing.append("예문 3 (비즈니스 - 생산, 구매, 품질, 연구 등)")
        if pd.isna(row['강조 포인트']): missing.append("강조 포인트 (실무 뉘앙스)")
        
        if not missing:
            continue
            
        exp = row['표현']
        meaning = row['뜻'] if not pd.isna(row['뜻']) else "문맥에 맞는 뜻"
        
        prompt = f"""
        영어 표현 '{exp}'(의미: {meaning})에 대해 다음 누락된 항목을 작성해.
        누락된 항목: {', '.join(missing)}
        
        [조건]
        1. 비즈니스 예문은 HR, 연구, 생산, 구매, 품질, 영업, 경영지원 등 다양한 실무 상황을 골고루 반영할 것.
        2. 강조 포인트는 이 표현이 실제 대화나 실무에서 어떤 뉘앙스로 쓰이는지 구체적으로 짚어줄 것.
        3. 아래의 '출력 형식'에 맞춰서 각 항목의 내용만 딱 출력할 것 (부연 설명 절대 금지).
        
        [출력 형식]
        예문 1: (영어 문장)
        예문 2: (영어 문장)
        예문 3: (영어 문장)
        강조 포인트: (한국어 설명)
        """
        
        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini", # 비용 효율적이고 빠르며 강력한 최신 모델
                max_tokens=300,
                messages=[{"role": "user", "content": prompt}]
            )
            
            result_text = response.choices[0].message.content
            
            for line in result_text.split('\n'):
                line = line.strip()
                if line.startswith('예문 1:') and pd.isna(row['예문 1']):
                    df.at[index, '예문 1'] = line.replace('예문 1:', '').strip()
                elif line.startswith('예문 2:') and pd.isna(row['예문 2']):
                    df.at[index, '예문 2'] = line.replace('예문 2:', '').strip()
                elif line.startswith('예문 3:') and pd.isna(row['예문 3']):
                    df.at[index, '예문 3'] = line.replace('예문 3:', '').strip()
                elif line.startswith('강조 포인트:') and pd.isna(row['강조 포인트']):
                    df.at[index, '강조 포인트'] = line.replace('강조 포인트:', '').strip()
                    
            update_callback(index + 1, len(df), exp, "생성 완료")
            time.sleep(0.5) 
            
        except Exception as e:
            update_callback(index + 1, len(df), exp, f"실패 (에러: {e})")
            
    return df