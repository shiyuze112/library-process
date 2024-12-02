import subprocess
import os


# 压缩视频到指定码率，并确保为H.264编码
def compress_video_to_bitrate(local_file_path: str, target_bitrate: int, uuid: str) -> str:
    """
    压缩指定路径的视频文件到目标码率，并保存为新的文件，确保编码为H.264。

    参数:
    local_file_path (str): 原视频文件的路径。
    target_bitrate (int): 目标视频码率（以Mbps为单位）。
    uuid (str): 用于生成输出文件名的唯一标识符。

    返回:
    str: 输出文件的路径。
    """
    output_file_path = local_file_path.rsplit('/', 1)[0] + f'/{uuid}.mp4'

    command = (
        f'ffmpeg -y -i {local_file_path} '
        f'-c:v libx264 -b:v {target_bitrate}M '
        f'-maxrate {target_bitrate * 1.5}M -bufsize {target_bitrate * 2}M '
        f'-preset slow -pass 1 -f null /dev/null && '
        f'ffmpeg -i {local_file_path} '
        f'-c:v libx264 -b:v {target_bitrate}M '
        f'-maxrate {target_bitrate * 1.5}M -bufsize {target_bitrate * 2}M '
        f'-preset slow -pass 2 {output_file_path}'
    )

    try:
        subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        os.remove(local_file_path)
    except subprocess.CalledProcessError as e:
        print(f"ffmpeg 错误信息：{e.stderr.decode()}")
        raise Exception(f"压缩视频时出错：{e}")

    return output_file_path

# if __name__ == "__main__":
#     local_file_path = '/Users/edy/Downloads/media/你好.mp4'
#     target_bitrate=3
#     uuid = 'e95c8ff9-fdf0-4cb4-b3c9-73ac253b9054'
#     compress_video_to_bitrate(local_file_path,target_bitrate,uuid)