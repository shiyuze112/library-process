import pandas as pd
import boto3
from concurrent.futures import ThreadPoolExecutor
from tqdm import tqdm
import logging
from app.config.settings import settings  # 假设这里存放着配置相关的内容，比如AWS的相关配置信息
import json

# 配置日志记录
logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(levelname)s | %(message)s')
logger = logging.getLogger(__name__)

# 获取S3存储桶名称
bucket_name = settings.AWS_BUCKET_NAME
# 创建S3客户端实例
try:
    s3 = boto3.client('s3')
except Exception as e:
    logger.error(f"创建S3客户端时出现错误: {str(e)}")
    raise

def check_key(key: str):
    try:
        s3.head_object(Bucket=bucket_name, Key=key)
        return True
    except Exception as e:
        logger.warning(f"检查对象键 {key} 时出现错误: {str(e)}")
        return False

# 读取CSV文件中的key字段值
csv_file_path = '/Users/edy/Downloads/media_rows-19.csv'
try:
    df = pd.read_csv(csv_file_path)
    unique_keys = df['key'].tolist()
except FileNotFoundError:
    logger.error(f"指定的CSV文件 {csv_file_path} 不存在，请检查文件路径是否正确。")
    raise
except Exception as e:
    logger.error(f"读取CSV文件 {csv_file_path} 时出现错误: {str(e)}")
    raise

unfound_keys = []
with ThreadPoolExecutor(max_workers=10) as executor:
    # 使用 list() 来确保所有任务完成，并使用 tqdm 显示进度
    try:
        results = list(tqdm(executor.map(check_key, unique_keys), total=len(unique_keys)))
    except Exception as e:
        logger.error(f"并发检查任务执行过程中出现错误: {str(e)}")
        raise
    # 将未找到的 key 添加到列表中
    unfound_keys = [key for key, exists in zip(unique_keys, results) if not exists]

print(f"总共有 {len(unfound_keys)} 个视频文件未找到")
print("未找到的文件 keys:")
for key in unfound_keys:
    print(key)

# 存储不符合条件的id
invalid_duration_ids = []
invalid_resolution_ids = []
invalid_size_ids = []
invalid_bps_ids = []
invalid_codec_ids = []
invalid_description_ids = []  # 新增存储无效description的列表

# 检查条件的函数
def check_duration(duration):
    return 1 <= duration <= 20

def check_resolution(height, width):
    return not (height < 720 and width < 720) and isinstance(height, int) and isinstance(width, int)

def check_size(size):
    return isinstance(size, float) and size < 30

def check_bps(bps):
    return isinstance(bps, float) and bps <= 7

def check_codec(codec):
    return codec == 'H.264'

def check_description(description):
    try:
        json.loads(description)  # 尝试加载为JSON
        return True
    except ValueError:
        return False  # 如果加载失败，返回False

# 遍历数据框进行检查
for index, row in df.iterrows():
    if not check_duration(row['duration']):
        invalid_duration_ids.append(row['id'])
    if not check_resolution(row['height'], row['width']):
        invalid_resolution_ids.append(row['key'])
    if not check_size(row['size']):
        invalid_size_ids.append(row['id'])
    if not check_bps(row['bps']):
        invalid_bps_ids.append(row['id'])
    if not check_codec(row['codec']):
        invalid_codec_ids.append(row['id'])
    if not check_description(row['description']):  # 检查description
        invalid_description_ids.append(row['id'])

# 输出不符合条件的id
if invalid_duration_ids:
    print(f"不符合 Duration: <= 20, >= 2 的行有: {invalid_duration_ids}")
if invalid_resolution_ids:
    print(f"不符合分辨率要求的行有: {invalid_resolution_ids}")
if invalid_size_ids:
    print(f"不符合 size < 30 的行有: {invalid_size_ids}")
if invalid_bps_ids:
    print(f"不符合 bps <= 6.5 的行有: {invalid_bps_ids}")
if invalid_codec_ids:
    print(f"不符合 codec 为 H.264 的行有: {invalid_codec_ids}")
if invalid_description_ids:
    print(f"不符合 description 格式的行有: {invalid_description_ids}")
# 输出不符合条件的id数量
if invalid_duration_ids:
    print(f"不符合 Duration: <= 20, >= 2 的行数量为: {len(invalid_duration_ids)}")
if invalid_resolution_ids:
    print(f"不符合分辨率要求的行数量为: {len(invalid_resolution_ids)}")
if invalid_size_ids:
    print(f"不符合 size < 30 的行数量为: {len(invalid_size_ids)}")
if invalid_bps_ids:
    print(f"不符合 bps <= 6.5 的行数量为: {len(invalid_bps_ids)}")
if invalid_codec_ids:
    print(f"不符合 codec 为 H.264 的行数量为: {len(invalid_codec_ids)}")
if invalid_description_ids:
    print(f"不符合 description 格式的行数量为: {len(invalid_description_ids)}")