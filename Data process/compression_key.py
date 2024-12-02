from video_bit_mem.get_info import get_video_info
from video_process.convert_video import process_video
from video_process.compress import compress_video
from upload.s3 import upload_video_to_s3
from upload.supabase import  update_video_w_h,update_video_compress,update_video_nocompress
from supabase import create_client
from dotenv import load_dotenv
import os
from logger import app_logger


# 加载环境变量
load_dotenv()
# Supabase 配置
url = os.getenv('URL')
key = os.getenv('KEY')
supabase = create_client(url, key)


def fetch_video_keys(page, page_size):
    """从 Supabase 获取video的 key 值和 uuid 值，支持翻页和排序。
    
    Args:
        page (int): 当前页码。
        page_size (int): 每页视频数量。
    
    Returns:
        list: 包含视频 key 和 uuid 的字典列表。
    """
    response = supabase.table('raw_media') \
     .select('key', 'uuid', 'status', 'key-uuid', 'description') \
     .eq('batch', '2') \
     .is_('key-uuid', None)\
     .is_('duration', None)\
     .filter('description', 'neq', '')\
     .order('key') \
     .range(page * page_size, (page + 1) * page_size - 1) \
     .execute()
    
    return [{'key': item['key'], 'uuid': item['uuid']} for item in response.data]



def process(key, uuid):
    """
    处理视频文件，包括下载、转换格式、压缩和上传。

    参数:
    key (str): S3 中视频文件的键（路径）。
    uuid (str): 视频的唯一标识符。

    返回:
    None
    """
    file_path = key 
    temp_file_path = None
    try:
        app_logger.info(f"访问文件: {file_path}")
        
        # 下载视频并获取信息
        width, height, duration, temp_file_path = get_video_info(file_path)
        
        app_logger.info(f"视频信息 - 宽度: {width}, 高度: {height}, 时长: {duration}秒，路径：{temp_file_path}")
        update_video_w_h(key, width, height,duration)#更新原始长宽时长
        # 使用本地路径进行处理
        try:
            if duration <= 20:
                # 如果视频时长小于等于20秒，进行压缩处理
                local_mp4_path = process_video(temp_file_path) # 将视频转换为mp4格式并改变分辨率
                bps, memory,width, height,codec, output_file_path, compress_key = compress_video(local_mp4_path, uuid)
                app_logger.info(f"处理后的视频 - 分辨率: {width}x{height}, 码率: {bps}, 内存: {memory}MB,编码格式为{codec}")
                upload_video_to_s3(output_file_path, compress_key)
                app_logger.info(f"文件 {compress_key} 上传成功。")
                update_video_compress(key, width, height, bps, memory, codec, compress_key)
                app_logger.info(f"文件 {key} 信息更新成功。")
                os.remove(output_file_path)
                app_logger.info(f"已删除路径为 {output_file_path} 的视频文件。")
                if temp_file_path:  # 检查 temp_file_path 是否为 None
                    os.remove(temp_file_path)
            else:
                app_logger.info(f"{temp_file_path}时长大于20s")
                if temp_file_path:  # 检查 temp_file_path 是否为 None
                    os.remove(temp_file_path)
                update_video_nocompress(key)
                
        except Exception as e:
            if temp_file_path:  # 检查 temp_file_path 是否为 None
                os.remove(temp_file_path)
            app_logger.error(f"在处理视频时发生错误：{e}")
    except Exception as e:
        if temp_file_path:  # 检查 temp_file_path 是否为 None
            os.remove(temp_file_path)
        app_logger.error(f"访问文件时发生错误: {e}")

if __name__ == "__main__":
    # 主程序
    page = 0
    page_size = 1000
    all_video_keys = []
    all_uuids = []
    while True:
        video_keys_with_uuids = fetch_video_keys(page, page_size)
        if not video_keys_with_uuids:
            break
        all_video_keys.extend([item['key'] for item in video_keys_with_uuids])
        all_uuids.extend([item['uuid'] for item in video_keys_with_uuids])
        page += 1

    # 直接处理视频，不使用多进程
    for key, uuid in zip(all_video_keys, all_uuids):  # 使用循环逐个处理视频
        process(key, uuid)  # 逐个调用处理函数
