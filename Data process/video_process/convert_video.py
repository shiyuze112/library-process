import os
from typing import Tuple
import moviepy.editor as mp
import cv2
import subprocess
def is_mp4_format(file_path: str) -> bool:
    return file_path.lower().endswith(".mp4")


def convert_to_mp4(local_file_path: str):
    """
    使用 FFmpeg 将视频文件转换为 MP4 格式。

    参数:
    local_file_path (str): 输入视频文件的路径。

    返回:
    str: 输出的 MP4 文件路径。
    """
    output_path = local_file_path.rsplit('.', 1)[0] + '.mp4'
    
    # 获取视频信息以调整分辨率
    probe_command = f'ffprobe -v error -select_streams v:0 -show_entries stream=width,height -of csv=p=0 "{local_file_path}"'
    width, height = subprocess.check_output(probe_command, shell=True).decode().strip().split(',')
    width, height = int(width), int(height)

    # 调整宽度和高度为偶数
    if width % 2 != 0:
        width += 1
    if height % 2 != 0:
        height += 1

    command = f'ffmpeg -i "{local_file_path}" -vf "scale={width}:{height}" -vcodec libx264 -acodec aac -preset medium -threads 4 "{output_path}"'
    try:
        result = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print(result.stdout.decode())  # 打印 FFmpeg 的标准输出
        return output_path
    except subprocess.CalledProcessError as e:
        print(f"使用 FFmpeg 转换视频时出错：{e}")
        print(e.stderr.decode())  # 打印 FFmpeg 的错误输出
        raise


# TODO


def get_video_size(local_file_path: str, output_path: str) -> tuple[int, int, int, int]:
    cap = cv2.VideoCapture(local_file_path)
    original_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    original_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    max_dimension = 1920
    secondary_dimension = 1080

    if original_width > original_height:
        # 横屏
        if original_width > max_dimension or original_height > secondary_dimension:
            aspect_ratio = original_width / original_height
            new_width = min(original_width, max_dimension)
            new_height = int(new_width / aspect_ratio)
            # 使用 OpenCV 写入视频（简单示例，可能需要更多参数调整）
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            out = cv2.VideoWriter(output_path, fourcc, 30.0, (new_width, new_height))
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                resized_frame = cv2.resize(frame, (new_width, new_height))
                out.write(resized_frame)
            out.release()
            return original_width, original_height, new_width, new_height
        else:
            # 如果不需要调整分辨率，则直接将视频写入 output_path
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            out = cv2.VideoWriter(output_path, fourcc, 30.0, (original_width, original_height))
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                out.write(frame)
            out.release()
            return original_width, original_height, original_width, original_height
    else:
        # 竖屏
        if original_height > max_dimension or original_width > secondary_dimension:
            aspect_ratio = original_height / original_width
            new_height = min(original_height, max_dimension)
            new_width = int(new_height / aspect_ratio)
            # 使用 OpenCV 写入视频（简单示例，可能需要更多参数调整）
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            out = cv2.VideoWriter(output_path, fourcc, 30.0, (new_width, new_height))
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                resized_frame = cv2.resize(frame, (new_width, new_height))
                out.write(resized_frame)
            out.release()
            return original_width, original_height, new_width, new_height
        else:
            # 如果不需要调整分辨率，则直接将视频写入 output_path
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            out = cv2.VideoWriter(output_path, fourcc, 30.0, (original_width, original_height))
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                out.write(frame)
            out.release()
            return original_width, original_height, original_width, original_height


def process_video(input_path: str) -> str:
    """
    处理视频：检查格式，获取尺寸，必要时调整大小并转换为MP4。

    参数:
    input_path (str): 输入视频文件的路径。

    返回:
    str: 输出MP4文件的路径。
    """
    
    output_path = f"/Users/edy/video-spider/22/data_manager/movies/{os.path.basename(input_path).replace(' ', '_').replace('(', '_').replace(')', '_')}"
    try:
        if not is_mp4_format(input_path):
            print(f"视频 {input_path} 不是MP4格式，将进行转换")
            mp4_path=convert_to_mp4(input_path)
            original_width, original_height, new_width, new_height = get_video_size(mp4_path, output_path)
            os.remove(mp4_path)
            print(f"调整视频大小从 {original_width}x{original_height} 到 {new_width}x{new_height}")
            
        else:
            print(f"视频 {input_path} 已是MP4格式，进行分辨率处理")
            original_width, original_height, new_width, new_height = get_video_size(input_path, output_path)
            print(f"调整视频大小从 {original_width}x{original_height} 到 {new_width}x{new_height}")
            
            # 这里可以添加调整分辨率的逻辑

        print(f"视频处理完成：{output_path}")
        return output_path  # 返回输出路径

    except Exception as e:
        print(f"处理视频 {input_path} 时出错：{e}")
        raise


# if __name__ == "__main__":
#     input_path = "/Users/edy/Movies/000873_VTXHD.mov"
    
#     process_video(input_path)
