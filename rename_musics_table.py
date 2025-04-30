import csv
import re
import os
import boto3
from video_core_client import test_core_api_client
from tqdm import tqdm
from botocore.exceptions import ClientError
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()
# S3配置
S3_CONFIG = {
    'aws_access_key_id': os.getenv('AWS_ACCESS_KEY_ID'),
    'aws_secret_access_key': os.getenv('AWS_SECRET_ACCESS_KEY'),
    'region_name': os.getenv('AWS_REGION'),
    'bucket': os.getenv('AWS_BUCKET')
}

# 验证环境变量是否都已设置
required_env_vars = ['AWS_ACCESS_KEY_ID', 'AWS_SECRET_ACCESS_KEY', 'AWS_REGION', 'AWS_BUCKET']
missing_vars = [var for var in required_env_vars if not os.getenv(var)]
if missing_vars:
    raise ValueError(f"缺少必要的环境变量: {', '.join(missing_vars)}\n请确保在.env文件中设置这些变量")


def get_s3_client():
    return boto3.client('s3',
                       aws_access_key_id=S3_CONFIG['aws_access_key_id'],
                       aws_secret_access_key=S3_CONFIG['aws_secret_access_key'],
                       region_name=S3_CONFIG['region_name'])


def copy_s3_file(old_key, new_key):
    """
    在S3上复制文件到新的路径
    """
    try:
        s3_client = get_s3_client()
        bucket = S3_CONFIG['bucket']
        
        # 构建复制源
        copy_source = {
            'Bucket': bucket,
            'Key': old_key
        }
        
        # 执行复制
        s3_client.copy_object(
            CopySource=copy_source,
            Bucket=bucket,
            Key=new_key
        )
        return True
    except ClientError as e:
        print(f"S3复制失败 - 从 {old_key} 到 {new_key}: {str(e)}")
        return False


def update_music_in_db(id, new_name, new_key):
    """
    更新数据库中的音乐信息
    """
    try:
        client = test_core_api_client
        update_data = {
            "name": new_name,
            "key": new_key
        }
        
        response = client.request(
            'POST',
            f'api/musics/update/{id}',
            json=update_data
        )
        
        if isinstance(response, dict) and response.get('code') == 200:
            return True
        else:
            print(f"更新数据库失败 - ID: {id}, 响应: {response}")
            return False
    except Exception as e:
        print(f"更新数据库出错 - ID: {id}, 错误: {str(e)}")
        return False


def process_updates(csv_file='music_data.csv'):
    """
    处理CSV文件中的更新
    """
    if not os.path.exists(csv_file):
        print(f"找不到CSV文件: {csv_file}")
        return
    
    success_count = 0
    fail_count = 0
    
    print("开始处理更新...")
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        
        for row in tqdm(rows, desc="更新进度"):
            try:
                id = row['id']
                old_key = row['key']
                new_name = row['new_name']
                new_key = row['new_key']
                
                if not all([id, old_key, new_name, new_key]):
                    print(f"警告: 数据不完整 - ID: {id}")
                    fail_count += 1
                    continue
                
                # 先在S3上复制文件
                if copy_s3_file(old_key, new_key):
                    # S3复制成功后，更新数据库
                    if update_music_in_db(id, new_name, new_key):
                        success_count += 1
                        continue
                    else:
                        print(f"警告: ID {id} 的S3复制成功但数据库更新失败，请手动检查")
                
                fail_count += 1
            except Exception as e:
                print(f"处理记录时出错 - ID: {id if 'id' in locals() else 'unknown'}, 错误: {str(e)}")
                fail_count += 1
            
    print("\n更新完成:")
    print(f"成功: {success_count}")
    print(f"失败: {fail_count}")
    print(f"总计: {len(rows)}")


def clean_name(name):
    if not isinstance(name, str):
        return ''
    # 去除.mp3后缀
    name = name.replace('.mp3', '')
    # 过滤特殊字符，只保留字母、数字、空格和一些基本标点
    cleaned_name = re.sub(r'[^\w\s\-\(\)]', '', name)
    return cleaned_name.strip()


def process_key(key, id):
    if not isinstance(key, str) or not key:
        return ''
    # 获取目录路径和文件名
    directory = os.path.dirname(key)
    # 使用id作为新的文件名
    new_key = os.path.join(directory, f"{id}.mp3")
    return new_key


def save_to_csv(musics, output_file='music_data.csv'):
    if not musics:
        print("没有数据需要保存")
        return

    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['id', 'name', 'key', 'new_name', 'new_key'])
        writer.writeheader()
        
        print("正在处理数据并保存到CSV...")
        for music in tqdm(musics, desc="处理音乐数据"):
            if isinstance(music, dict):
                name = music.get('name', '')
                key = music.get('key', '')
                id = music.get('id', '')
                
                if not all([name, key, id]):
                    print(f"警告: 数据不完整 - ID: {id}, Name: {name}, Key: {key}")
                    continue
                
                new_name = clean_name(name)
                new_key = process_key(key, id)
                
                writer.writerow({
                    'id': id,
                    'name': name,
                    'key': key,
                    'new_name': new_name,
                    'new_key': new_key
                })


def get_musics_by_pagination():
    # 初始化客户端
    client = test_core_api_client
    page = 1  # 初始页码
    limit = 1000 # 每页条数
    max_retries = 3  # 最大重试次数
    all_musics = []

    print("开始获取音乐数据...")
    with tqdm(desc="获取分页数据", unit="页") as pbar:
        while True:
            try:
                retries = 0
                while retries < max_retries:
                    try:
                        # 构建查询字符串
                        query_string = f"?page={page}&limit={limit}"
                        # 发送 GET 请求获取数据
                        response = client.request('GET', f'api/musics/pagination{query_string}')
                        
                        # 从响应中获取音乐列表
                        if isinstance(response, dict):
                            if 'data' in response:
                                music_list = response['data']
                                if not music_list:  # 如果没有更多数据
                                    print("\n已获取所有数据")
                                    return all_musics
                                all_musics.extend(music_list)
                                pbar.update(1)
                                page += 1
                                break
                            else:
                                print("\n响应格式不正确，缺少 'data' 字段")
                                print(f"响应内容: {response}")
                                return all_musics
                        else:
                            print(f"\n响应不是字典格式: {response}")
                            return all_musics
                            
                    except Exception as e:
                        if "Read timed out" in str(e):
                            retries += 1
                            print(f"\n请求超时，正在进行第 {retries} 次重试...")
                        else:
                            print(f"\n发生未知错误: {str(e)}")
                            return all_musics

                if retries == max_retries:
                    print("\n达到最大重试次数，请求失败")
                    return all_musics

            except Exception as e:
                print(f"\n请求发生错误: {str(e)}")
                return all_musics

    return all_musics


if __name__ == "__main__":
    result = get_musics_by_pagination()
    print(f"\n总共获取到 {len(result)} 条音乐数据")
    save_to_csv(result)
    print("数据已保存备份到 music_data.csv 文件中")
    process_updates() 