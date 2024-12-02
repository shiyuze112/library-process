import os
import subprocess
from typing import Tuple
import boto3
import cv2
from moviepy.editor import VideoFileClip
from dotenv import load_dotenv
from upload.supabase import update_video_nocompress

# 加载环境变量
load_dotenv()
# S3 配置
s3_client = boto3.client(
    's3',
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
    region_name=os.getenv('AWS_REGION')  # 使用环境变量
)
bucket_name = os.getenv('BUCKET_NAME') 

def get_video_info(file_path):
    """
    从本地路径获取视频文件信息，包括宽度、高度和持续时间，并将文件写入临时路径。

    参数:
    file_path (str): 本地视频文件的路径。

    返回:
    tuple: 包含视频宽度、高度、持续时间和临时文件路径的元组。
    """
    # 检查本地文件是否存在
    if not os.path.exists(file_path):
        return None  # 文件不存在时返回 None，避免输出错误信息
    
    # # 检查文件大小
    # file_size = os.path.getsize(file_path)
    # if file_size > 400 * 1024 * 1024:
    #     raise Exception(f"视频文件 {file_path} 大于500MB，不会处理。")
    
    # 创建临时文件路径
    file_name = os.path.basename(file_path)
    temp_file_path = f'/Users/edy/video-spider/22/data_manager/test_videos/{file_name}'
    
    # 将本地文件写入临时文件路径
    with open(file_path, 'rb') as source_file:
        with open(temp_file_path, 'wb') as temp_file:
            temp_file.write(source_file.read())
    
    # 使用 OpenCV 获取视频信息
    cap = cv2.VideoCapture(temp_file_path)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    duration = frame_count / fps if fps > 0 else 0
    
    return width, height, duration, temp_file_path


def get_video_bitrate_and_memory(local_file_path: str) -> Tuple[float, float, int, int, str]:
    """
    获取视频的码率、内存使用情况和编码格式。

    参数:
    local_file_path (str): 视ео文件的本地路径。

    返回:
    tuple: 包含视频码率（Mbps）、文件大小（MB）、视频宽度、高度和编码格式的元组。
    """
    # 使用 ffprobe 获取视频信息
    command = [
        'ffprobe',
        '-v', 'error',
        '-select_streams', 'v:0',
        '-show_entries', 'stream=bit_rate,width,height,codec_name',
        '-of', 'default=noprint_wrappers=1:nokey=1',
        local_file_path
    ]
    try:
        output = subprocess.check_output(command).strip().decode('utf-8')
        codec,width,height,bitrate=output.split('\n')
    except subprocess.CalledProcessError as e:
        raise Exception(f"获取码率时出错：{e}")

    # 获取视频文件大小（MB）
    memory_size = os.path.getsize(local_file_path) / (1024 * 1024)  # 转换为 MB

    # 将比特率从 bits/s 转换为 Mbps
    bitrate_mbps = float(bitrate)/ 1_000_000

    return bitrate_mbps, memory_size, int(width), height, codec 
