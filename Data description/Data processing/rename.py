import os
import pandas as pd
import shutil
import json


# 设置路径
media_path = '/Volumes/XDISK/video-1'
xlsx_path = '/Volumes/XDISK/素材库信息记录.xlsx'  
json_path = '/Users/edy/video-spider/data-label/Data processing/rename_dict.json'  
df = pd.read_excel(xlsx_path)
folder_names = df['素材库在网盘中的文件夹名称'].astype(str).tolist()
id_values = df['ID'].astype(str).tolist()  # 如果需要ID也是字符串
rename_dict = dict(zip(folder_names, id_values))

# 保存重命名字典为JSON文件
with open(json_path, 'w', encoding='utf-8') as json_file:
    json.dump(rename_dict, json_file, ensure_ascii=False, indent=4)
print(f"重命名字典已保存为JSON文件: {json_path}")

# 删除指定后缀的文件和空文件夹
for root, dirs, files in os.walk(media_path, topdown=False):
    for file in files:
        if file.endswith(('.url', '.txt', '.jpg','png')):
            file_path = os.path.join(root, file)
            try:
                os.remove(file_path)
                print(f"删除文件: {file_path}")
            except FileNotFoundError:
                print(f"文件不存在，无法删除: {file_path}")

    # 删除空文件夹
    if not os.listdir(root):  # 如果文件夹为空
        try:
            os.rmdir(root)
            print(f"删除空文件夹: {root}")
        except OSError:
            print(f"无法删除非空文件夹: {root}")


# 读取 JSON 文件
with open(json_path, 'r', encoding='utf-8') as json_file:
    rename_dict = json.load(json_file)

# 重命名文件夹
for item in os.listdir(media_path):
    folder_path = os.path.join(media_path, item)
    if os.path.isdir(folder_path):
        current_folder_name = item.strip()
        matched = False
        for key in rename_dict.keys():
            key = key.strip()
            if key.startswith(current_folder_name) or current_folder_name in key:
                new_folder_name = rename_dict[key]
                new_folder_path = os.path.join(media_path, new_folder_name)
                shutil.move(folder_path, new_folder_path)
                print(f"重命名文件夹: {current_folder_name} -> {new_folder_name}")
                matched = True
                break  
        if not matched:
            print(f"未找到匹配项: {current_folder_name}")
            
print("操作完成！")
