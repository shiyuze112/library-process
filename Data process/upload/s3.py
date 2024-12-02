import boto3
import os
import time
from logger import app_logger

# S3 配置
s3_client = boto3.client(
    's3',
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
    region_name=os.getenv('AWS_REGION')  # 使用环境变量
)

def upload_video_to_s3(output_file_path, key3):
    """
    将视频文件上传到 S3 存储桶。

    参数:
    output_file_path (str): 要上传的视频文件的本地路径。
    key3 (str): 在 S3 中存储文件的键（路径）。

    返回:
    None
    """
    bucket_name = os.getenv('BUCKET_NAME') 
    s3 = boto3.client('s3')
    s3_key = key3
    retries = 3  # 设置重试次数
    for attempt in range(retries):
        try:
            s3.upload_file(output_file_path, bucket_name, s3_key)
            app_logger.info(f"Uploaded {output_file_path} to {bucket_name}/{s3_key}")
            break  # 成功上传后退出循环
        except Exception as e:
            app_logger.error(f"Error uploading {output_file_path}: {e}")
            if attempt < retries - 1:  # 如果不是最后一次尝试，等待一段时间再重试
                time.sleep(2)  # 等待 2 秒再重试
