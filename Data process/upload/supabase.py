import os
import time
from dotenv import load_dotenv
from supabase import create_client

# 加载环境变量
load_dotenv()
# Supabase 配置
url = os.getenv('URL')
key = os.getenv('KEY')
supabase = create_client(url, key)

def update_video_w_h(key, width, height, duration, retries=3, delay=2):
    """
    更新 Supabase 中的视频信息

    参数:
    key (str): 视频的唯一标识符
    width (int): 视频的宽度
    height (int): 视频的高度
    retries (int): 重试次数
    delay (int): 重试延迟（秒）
    """
    for attempt in range(retries):
        try:
            # 更新 Supabase 中的视频信息
            supabase.table('raw_media').update({
                'width': width,
                'height': height,
                'duration': duration,
            }).eq('key', key).execute()
            break  # 成功后退出循环
        except Exception as e:
            if attempt < retries - 1:  # 如果不是最后一次尝试
                time.sleep(delay)  # 等待后重试
            else:
                raise e  # 抛出最后一次的异常

def update_video_compress(key, cpsw, cpsh, bps, memory, codec, key_uuid, retries=3, delay=2):
    """
    更新 Supabase 中的视频信息

    参数:
    key (str): 视频的唯一标识符
    cpsw (int): 视频的压缩宽度
    cpsh (int): 视频的压缩高度
    bps (int): 视频的比特率
    codec (str): 视频的编码格式
    memory (int): 视频所需的内存
    key_uuid (str): s3视频路径信息
    status: 处理状态
    retries (int): 重试次数
    delay (int): 重试延迟（秒）
    """
    for attempt in range(retries):
        try:
            # 更新 Supabase 中的视频信息
            supabase.table('raw_media').update({
                'cps-w': cpsw,
                'cps-h': cpsh,
                'bps': bps,
                'size': memory,
                'codec': codec,
                'key-uuid': key_uuid,
                "status": "processed"  # status: processed, unprocessed
            }).eq('key', key).execute()
            break  # 成功后退出循环
        except Exception as e:
            if attempt < retries - 1:  # 如果不是最后一次尝试
                time.sleep(delay)  # 等待后重试
            else:
                raise e  # 抛出最后一次的异常

def update_video_nocompress(key, retries=3, delay=2):
    """
    更新 Supabase 中的视频信息

    参数:
    key (str): 视频的唯一标识符
    status: 处理状态
    retries (int): 重试次数
    delay (int): 重试延迟（秒）
    """
    for attempt in range(retries):
        try:
            # 更新 Supabase 中的视频信息
            supabase.table('raw_media').update({
                'status': "unprocessed"
            }).eq('key', key).execute()
            break  # 成功后退出循环
        except Exception as e:
            if attempt < retries - 1:  # 如果不是最后一次尝试
                time.sleep(delay)  # 等待后重试
            else:
                raise e  # 抛出最后一次的异常
