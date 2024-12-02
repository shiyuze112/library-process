from supabase import create_client
from MODE.VOICEmode import ask_llm_description
import time
from multiprocessing import Pool, cpu_count
import os
from dotenv import load_dotenv
load_dotenv()

url = os.getenv("URL")
key = os.getenv("KEY")
supabase = create_client(url, key)

# 包装请求函数，带有重试机制
def execute_with_retry(request_func, retries=5, delay=10):
    for i in range(retries):
        try:
            return request_func()
        except Exception as e:
            print(f"错误发生，正在重试 ({i + 1}/{retries})，错误: {e}")
            time.sleep(delay)
    print("多次重试后失败，跳过此步骤。")
    return None

# 处理音乐的函数
def process_music(row):
    role_name = row['role_name']
    gender = row['gender_en']
    age = row['age_en']
    language = row['language_en']
    description = row['voice_description_en']
    style = row['voice_style_en']
    field = row['voice_field_en']
    ID = row['ID']
    # 调用函数生成描述（重试机制）
    response_des = execute_with_retry(lambda: ask_llm_description(role_name, gender, age, language, description, style, field, model="gpt-4o-mini"))

    # 检查结果
    if not response_des:
        print(f"无法生成描述，跳过: {ID}")
        
        # 更新 Supabase 表中的 label 列
        # execute_with_retry(lambda: supabase.table('voice').update({
        #     'label': 'not description'
        # }).eq('key', row['key']).execute())
        return

    # 清理格式
    response_des = response_des.strip('```json').strip('```').strip()
    # print(response_des)
    # try:
    #     # 确保返回值是有效的JSON格式
    #     response_des = json.loads(response_des) if response_des else None
    # except json.JSONDecodeError as e:
    #     print(f"JSON解码失败，跳过音乐: {ID}，错误: {e}")
    #     return
    # print(response_des)
    # 更新Supabase表中的数据
    update_success = execute_with_retry(lambda: supabase.table('voice').update({
        'description': response_des
    }).eq('id', row['id']).execute())
    if update_success:
        print(f"成功更新Supabase表，音乐: {ID}")
    else:
        print(f"更新Supabase表失败，跳过音乐: {ID}")

def process_musics():
    page_size = 100  # 每页提取的数据量
    offset = 0

    while True:
        # 从Supabase获取音乐信息
        data = supabase.table('voice').select('id, ID, role_name, gender_en, age_en, language_en, voice_description_en, voice_style_en, voice_field_en').is_('description', None).limit(page_size).offset(offset).execute()
        
        # 使用 data.data 访问实际数据
        music_rows = data.data

        if not music_rows:
            # 如果没有更多数据，退出循环
            break

        # 使用多进程处理音乐
        with Pool(min(cpu_count(), 4)) as pool:  # 限制最大进程数为4
            pool.map(process_music, music_rows)

        # 更新偏移量
        offset += page_size

# 执行主处理逻辑
if __name__ == "__main__":
    try:
        process_musics()
    except Exception as e:
        print(f"程序发生错误: {e}")
