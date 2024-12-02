import os
import boto3
import cv2
import json
from supabase import create_client
from MODE.VIDEOmode import ask_llm_description
import time
from multiprocessing import Pool, current_process, cpu_count
from dotenv import load_dotenv
load_dotenv()

url = os.getenv("URL")
key = os.getenv("KEY")
supabase = create_client(url, key)
# 初始化S3客户端
s3_client = boto3.client(
    's3',
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
    region_name=os.getenv('AWS_REGION')
)

# 定义本地目录路径和S3桶名称
bucket_name = os.getenv('S3_BUCKET_NAME')
local_dir = '/Users/edy/video-spider/video'

# 定义截图函数
def take_screenshots(video_path, output_dir, num_screenshots, video_key):
    cap = cv2.VideoCapture(video_path)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    screenshot_paths = []

    # 获取当前进程ID
    process_id = current_process().pid
    for i in range(num_screenshots):
        frame_number = int((i * total_frames) / num_screenshots)
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
        ret, frame = cap.read()
        if ret:
            screenshot_path = os.path.join(output_dir, f'screenshot_{process_id}_{i + 1}.jpg')
            cv2.imwrite(screenshot_path, frame)
            screenshot_paths.append(screenshot_path)
            print(f"正在处理视频 key: {video_key}，已生成截图: {screenshot_path}")
    cap.release()
    return screenshot_paths

# 包装请求函数，带有重试机制
def execute_with_retry(request_func, retries=5, delay=5, request_interval=5):
    for i in range(retries):
        try:
            time.sleep(request_interval)  # 在每次请求前等待固定时间
            return request_func()
        except Exception as e:
            if "token rate limit" in str(e):  # 检查是否是速率限制错误
                print("达到令牌速率限制，等待更长时间再重试...")
                time.sleep(30)  # 增加等待时间
            else:
                print(f"错误发生，正在重试 ({i + 1}/{retries})，错误: {e}")
                time.sleep(delay)
    print("多次重试后失败，跳过此步骤。")
    return None

# def download_video_with_check(bucket_name, video_key, local_video_path):
#     try:
#         # 下载文件
#         s3_client.download_file(bucket_name, video_key, local_video_path)
#         # 检查文件是否存在
#         if os.path.exists(local_video_path):
#             # 检查文件是否可读
#             cap = cv2.VideoCapture(local_video_path)
#             if cap.isOpened():
#                 cap.release()
#                 print(f"视频 {video_key} 成功下载并验证通过。")
#                 return True
#             else:
#                 print(f"下载的文件无法打开或读取: {local_video_path}")
#                 cap.release()
#                 os.remove(local_video_path)  # 删除下载失败的视频
#         else:
#             print(f"下载失败，文件不存在: {local_video_path}")
#     except Exception as e:
#         print(f"下载视频时发生错误: {video_key}，错误: {e}")
#     return False

# 主处理逻辑
def process_video(row):
    video_key = row['key']
    library_name = row['library_name_en']
    topic = row['topic_en']
    category_2 = row['category_2_en']
    # duration= row['duration']

    # # 下载视频到本地
    # local_video_path = os.path.join(local_dir, os.path.basename(video_key))
    # if not download_video_with_check(bucket_name, video_key, local_video_path):
    #     print(f"下载视频失败，跳过视频: {video_key}")
    #     return
    local_video_path=row['key']
    def get_video_duration(local_video_path):
        cap = cv2.VideoCapture(local_video_path)
        if not cap.isOpened():
            print(f"无法打开视频文件: {local_video_path}")
            # 更新 Supabase 表中的 label 列
            execute_with_retry(lambda: supabase.table('raw_media').update({
                'status': 'unprocessed'
            }).eq('key', video_key).execute())
            return 0
        fps = cap.get(cv2.CAP_PROP_FPS)
        frame_count = cap.get(cv2.CAP_PROP_FRAME_COUNT)
        duration = frame_count / fps
        cap.release()
        return duration

    duration = get_video_duration(local_video_path)
    num_screenshots = 3 if duration <= 5 else 4 if duration <= 10 else 6
    
    # 进行截图
    image_paths = execute_with_retry(lambda: take_screenshots(local_video_path, local_dir, num_screenshots, video_key))
    if not image_paths:
        print(f"生成截图失败，跳过视频: {video_key}")
        # os.remove(local_video_path)  # 删除下载失败的视频
        return

    # 准备调用函数的参数
    video_name = library_name
    keywords = topic
    categories = category_2

    # 调用函数生成关键词和描述（重试机制）
    # response_key = execute_with_retry(lambda: ask_llm_keyword(image_paths, video_name, keywords, categories, model="gpt-4o-mini"))
    response_des = execute_with_retry(lambda: ask_llm_description(image_paths, video_name, keywords, categories, model="gpt-4o-mini"), request_interval=5)

    # 检查结果
    if not response_des:
        print(f"无法生成关键词或描述，跳过该视频: {video_key}")
        
        # 更新 Supabase 表中的 label 列
        # execute_with_retry(lambda: supabase.table('raw_media').update({
        #     'status': 'unprocessed'
        # }).eq('key', video_key).execute())
        
        # os.remove(local_video_path)  # 删除下载失败的视频
        for image_path in image_paths:
            os.remove(image_path)  # 删除生成失败的截图
        return

    # 清理格式
    # response_key = response_key.strip('```json').strip('```').strip()
    response_des = response_des.strip('```json').strip('```').strip()
    try:
        # 确保返回值是有效的JSON格式
        # response_key = json.loads(response_key) if response_key else None
        response_des = json.loads(response_des) if response_des else None
    except json.JSONDecodeError as e:
        print(f"JSON解码失败，跳过视频: {video_key}，错误: {e}")
        # os.remove(local_video_path)  # 删除下载失败的视频
        for image_path in image_paths:
            os.remove(image_path)  # 删除生成失败的截图
        return

    # 清理临时文件
    # os.remove(local_video_path)
    for image_path in image_paths:
        os.remove(image_path)

    # 更新Supabase表中的数据
    update_success = execute_with_retry(lambda: supabase.table('raw_media').update({
        'description': response_des
    }).eq('key', video_key).execute())
    if update_success:
        print(f"成功更新Supabase表,视频: {video_key}")
    else:
        print(f"更新Supabase表失败,跳过视频: {video_key}")

def process_videos():
    # 从Supabase获取视频信息
    data = supabase.table('raw_media').select('key, library_name_en, topic_en, category_2_en').eq('batch', '2').is_('description', None).execute()
    
    # 使用 data.data 访问实际数据
    video_rows = data.data
    
    # 过滤掉以 .wav 或 .mp3 结尾的音频文件
    filtered_video_rows = [row for row in video_rows if not row['key'].lower().endswith(('.wav', '.mp3', '.txt', 'url','.link','.mhtml','lnk'))]

    # 使用多进程处理视频
    with Pool(min(cpu_count(), 4)) as pool:  # 限制最大进程数为4
        pool.map(process_video, filtered_video_rows)

# 执行主处理逻辑
if __name__ == "__main__":
    try:
        process_videos()
    except Exception as e:
        print(f"程序发生错误: {e}")
