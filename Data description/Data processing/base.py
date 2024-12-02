import os
import json
import pandas as pd
from datetime import datetime
from collections import defaultdict
from supabase import create_client
import uuid 
from dotenv import load_dotenv
load_dotenv()
def list_files_in_directory(directory_path, current_path=""):
    try:
        # 检查目录是否存在
        if not os.path.exists(directory_path):
            print(f"目录 {directory_path} 不存在")
            return

        # 获取目录下的所有文件和子目录
        for item in os.listdir(directory_path):
            # 构建完整路径
            full_path = os.path.join(directory_path, item)

            # 如果是文件，输出完整路径
            if os.path.isfile(full_path) and not item.startswith('.'):
                # 替换路径前缀
                yield full_path
            # 如果是目录，递归调用
            elif os.path.isdir(full_path):
                yield from list_files_in_directory(full_path)

    except Exception as e:
        print(f"发生错误: {e}")

def extract_matching_rows(excel_path, file_paths):
    # 读取Excel文件
    df = pd.read_excel(excel_path, engine='openpyxl')
    
    # 初始化结果列表和统计字典
    result = []
    stats = defaultdict(int)
    
    # 遍历文件路径
    for file_path in file_paths:
        # 提取library_id
        library_id = file_path.split('/')[4]
        # 查找匹配的行
        matching_rows = df[df['ID'] == library_id]
        
        # 提取所需列值并生成uuid
        for index, row in matching_rows.iterrows():
            entry = {
                'library_name': row['素材库名称'],
                'library_id': row['ID'],
                'source_import_path': row['素材库在网盘中的文件夹名称'],
                'type': "video/mp4",
                'tags': row['视频特点'].split(', ') if pd.notna(row['视频特点']) else [],
                'watermark': True if row['是否有水印'] == '是' else False if pd.notna(row['是否有水印']) else None,
                'topic': row['题材'].split(', ') if pd.notna(row['题材']) else [],
                'category_1': row['品类'],
                'category_2': row['主题'],
                'entry_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'key': file_path,
                'uuid': str(uuid.uuid4())  # 生成并添加uuid
            }
            result.append(entry)
            stats[library_id] += 1
    
    return result, stats


# 指定目录路径
directory_path = "/Volumes/XDISK/video-1"
excel_path = "/Volumes/XDISK/素材库信息记录.xlsx"

# 获取文件路径
file_paths = list(list_files_in_directory(directory_path))

# 提取匹配行
result, stats = extract_matching_rows(excel_path, file_paths)

# 将结果保存到JSON文件
output_file_path = "/Users/edy/video-spider/data-label/Data processing//output.json"
with open(output_file_path, 'w', encoding='utf-8') as json_file:
    json.dump(result, json_file, ensure_ascii=False, indent=4)

print(f"结果已保存到 {output_file_path}")
# 输出统计结果
print("\\\\n统计结果:")
for library_id, count in stats.items():
    print(f"文件夹 {library_id} 共写入了 {count} 个文件")



url = os.getenv("URL")
key = os.getenv("KEY")
supabase = create_client(url, key)

# 插入数据到 Supabase，并更新uuid字段
for entry in result:
    data = {
        'library_name': entry['library_name'],
        'library_id': entry['library_id'],
        'source_import_path': entry['source_import_path'],
        'type': entry['type'],
        'tags': entry['tags'],
        'watermark': entry['watermark'],
        'topic': entry['topic'],
        'category_1': entry['category_1'],
        'category_2': entry['category_2'],
        'entry_date': entry['entry_date'],
        'key': entry['key'],
        'batch': "2",
        'uuid': entry['uuid'] # 添加uuid字段并生成随机uuid
    }
    response = supabase.table('raw_media').insert(data).execute()
    if response.data is None:
        # 仅在发生错误时输出错误的数据
        print(f"插入数据时发生错误: {response}, 错误的数据: {data}")
    else:
        print(f"成功插入数据: {data}")

print("数据已成功插入到 Supabase 数据库中")
