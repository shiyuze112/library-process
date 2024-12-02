import os
import openai
from dotenv import load_dotenv
import json
import base64

# 加载环境变量
def initialize_openai():
    load_dotenv()
    openai.api_type = "azure"
    openai.api_base = "https://one2x-east-us-test.openai.azure.com/"
    openai.api_version = "2023-03-15-preview"
    openai.api_key = os.getenv("AZURE_OPENAI_API_KEY")

# 图像转为 Base64
def encode_image_to_base64(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

# 构建消息
# def build_messages_keyword(image_paths, video_name, keywords, categories):
    # with open("keyword_video_multi_frames_en_1126.json", "r", encoding="utf-8") as file:
    #     config = json.load(file)
    
    # system_prompt = config["systemPrompt"]
    # messages = [{"role": "system", "content": system_prompt}]
    
    # for idx, img_path in enumerate(image_paths):
    #     image_base64 = encode_image_to_base64(img_path)
    #     messages.append({
    #         "role": "user",
    #         "content": [{
    #             "type": "image_url",
    #             "image_url": {"url": f"data:image/jpeg;base64,{image_base64}"},
    #         }],
    #     })
    
    # messages.append({"role": "user", "content": f"视频名称: {video_name}"})
    # messages.append({"role": "user", "content": f"视频关键词: {keywords}"})
    # messages.append({"role": "user", "content": f"适合的视频品类: {categories}"})
    
    # return messages
def build_messages_description(image_paths, video_name, keywords, categories):
    with open("description_video_multi_frames_en_1129.json", "r", encoding="utf-8") as file:
        config = json.load(file)
    
    system_prompt = config["systemPrompt"]
    messages = [{"role": "system", "content": system_prompt}]
    
    for idx, img_path in enumerate(image_paths):
        image_base64 = encode_image_to_base64(img_path)
        messages.append({
            "role": "user",
            "content": [{
                "type": "image_url",
                "image_url": {"url": f"data:image/jpeg;base64,{image_base64}"},
            }],
        })
    
    messages.append({"role": "user", "content": f"视频名称: {video_name}"})
    messages.append({"role": "user", "content": f"视频关键词: {keywords}"})
    messages.append({"role": "user", "content": f"适合的视频品类: {categories}"})
    
    return messages

# 请求处理
# def ask_llm_keyword(image_paths, video_name, keywords, categories, model="gpt-4o-mini"):
    # try:
    #     # 初始化OpenAI配置
    #     initialize_openai()
        
    #     # 构建消息
    #     messages = build_messages_keyword(image_paths, video_name, keywords, categories)
        
    #     # 载入JSON配置文件
    #     with open("keyword_video_multi_frames_en.json", "r", encoding="utf-8") as file:
    #         config = json.load(file)
        
    #     # 发送请求
    #     response = openai.ChatCompletion.create(
    #         engine=model,
    #         messages=messages,
    #         max_tokens=config["chatParameters"]["maxResponseLength"],
    #         temperature=config["chatParameters"]["temperature"],
    #         top_p=config["chatParameters"]["topProbablities"]
    #     )
        
    #     # 返回结果
    #     return response.choices[0].message['content']
    
    # except openai.error.OpenAIError as e:
    #     print(f"OpenAI API Error: {str(e)}")
    #     return None
    # except Exception as e:
    #     print(f"Unexpected Error: {str(e)}")
    #     return None

def ask_llm_description(image_paths, video_name, keywords, categories, model="gpt-4o-mini"):
    try:
        # 初始化OpenAI配置
        initialize_openai()
        
        # 构建消息
        messages = build_messages_description(image_paths, video_name, keywords, categories)
        
        # 载入JSON配置文件
        with open("description_video_multi_frames_en_1129.json", "r", encoding="utf-8") as file:
            config = json.load(file)
        
        # 发送请求
        response = openai.ChatCompletion.create(
            engine=model,
            messages=messages,
            max_tokens=config["chatParameters"]["maxResponseLength"],
            temperature=config["chatParameters"]["temperature"],
            top_p=config["chatParameters"]["topProbablities"]
        )
        
        # 返回结果
        return response.choices[0].message['content']
    
    except openai.error.OpenAIError as e:
        print(f"OpenAI API Error: {str(e)}")
        return None
    except Exception as e:
        print(f"Unexpected Error: {str(e)}")
        return None

# 示例调用
if __name__ == "__main__":
    # 示例输入
    image_paths = [
        "/Users/edy/Downloads/63271732616348_.pic_hd.jpg",
    ]
    video_name = ""
    keywords = ""
    categories = [""]

    # 调用函数
    # print("Testing ask_llm function...11111111")
    # response = ask_llm_keyword(image_paths, video_name, keywords, categories, model="gpt-4o-mini")
    # print("Response from ask_llm:", response)
    print("Testing ask_llm function...")
    response = ask_llm_description(image_paths, video_name, keywords, categories, model="gpt-4o-mini")
    print("Response from ask_llm:", response)
