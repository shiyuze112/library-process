import os
import subprocess
from typing import Dict
from video_bit_mem.get_info import get_video_bitrate_and_memory
from video_bit_mem.compress_video import compress_video_to_bitrate

# 新增的函数：压缩视频
def compress_video(local_file_path: str, uuid: str) -> Dict[str, str]:
    """压缩视频函数
    参数:
    local_file_path: 视频文件的本地路径
    uuid: 视频的唯一标识符

    get_video_bitrate_and_memory():视频当前的码率、内存、分辨率
    compress_video_to_bitrate():对视频进行码率降低处理
    
    返回:
    width: 处理后的视频分辨率宽度
    height: 处理后的视频分辨率高度
    current_bitrate: 当前码率
    memory_size: 视频内存大小
    output_file_path: 输出视频文件的路径
    key_compress: s3视频资源路径
    """
    # 获取原始视频的宽度、高度、码率和内存大小
    try:
        current_bitrate, memory_size, width, height, codec = get_video_bitrate_and_memory(local_file_path)
        print(f"原始码率为{current_bitrate},内存为{memory_size},分辨率为{width}*{height},编码格式为{codec}")
    except Exception as e:
        raise Exception(f"获取视频信息时出错：{e}")

    
    compress_key = f"medeo/resource/video/2/{uuid}.mp4"
    # 如果码率小于 6，直接返回
    if current_bitrate <= 6:
        print("码率小于等于 6,不需要处理。")
        # 直接将local_file_path路径的视频重命名为uuid.mp4
        output_file_path = local_file_path.rsplit('/', 1)[0] + f'/{uuid}.mp4'
        subprocess.run(['ffmpeg', '-i', local_file_path, '-c:v', 'libx264', output_file_path], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        os.remove(local_file_path)
        current_bitrate, memory_size, width, height, codec = get_video_bitrate_and_memory(output_file_path)
        print(f"处理后编码格式为{codec}")
        return current_bitrate, memory_size, width, height,codec, output_file_path, compress_key
    else:
    # 如果码率大于 6，处理成 6 码率
        current_bitrate = 6
        output_file_path = compress_video_to_bitrate(local_file_path, current_bitrate, uuid)
        current_bitrate, memory_size, width, height, codec = get_video_bitrate_and_memory(output_file_path)
        print(f"处理后码率为{current_bitrate},内存为{memory_size},分辨率为{width}*{height},编码格式为{codec}")
        return current_bitrate, memory_size, width, height,codec, output_file_path, compress_key

# if __name__ == "__main__":
#     local_file_path = '/Users/edy/Downloads/media/你好.mp4'
#     uuid = 'e95c8ff9-fdf0-4cb4-b3c9-73ac253b9054'
#     compress_video(local_file_path,uuid)
