import os
import openai
from dotenv import load_dotenv
import json

# 加载环境变量
def initialize_openai():
    load_dotenv()
    openai.api_type = "azure"
    openai.api_base = "https://one2x-east-us-test.openai.azure.com/"
    openai.api_version = "2023-03-15-preview"
    openai.api_key = os.getenv("AZURE_OPENAI_API_KEY")


# 构建消息
def build_messages_description(video_name, categories):
    with open("description_bgm_en.json", "r", encoding="utf-8") as file:
        config = json.load(file)
    
    system_prompt = config["systemPrompt"]
    messages = [{"role": "system", "content": system_prompt}]
    
    
    messages.append({"role": "user", "content": f"视频名称: {video_name}"})
    messages.append({"role": "user", "content": f"适合的视频品类: {categories}"})
    
    return messages

# 请求处理
def ask_llm_description(video_name, categories, model="gpt-4o-mini"):
    try:
        # 初始化OpenAI配置
        initialize_openai()
        
        # 构建消息
        messages = build_messages_description(video_name, categories)
        
        # 载入JSON配置文件
        with open("description_bgm_en.json", "r", encoding="utf-8") as file:
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


# 构建消息
def build_messages_description1(video_name):
    with open("description_bgm_en.json", "r", encoding="utf-8") as file:
        config = json.load(file)
    
    system_prompt = config["systemPrompt"]
    messages = [{"role": "system", "content": system_prompt}]
    
    
    messages.append({"role": "user", "content": f"视频名称: {video_name}"})
    
    return messages

# 请求处理
def ask_llm_description1(video_name, model="gpt-4o-mini"):
    try:
        # 初始化OpenAI配置
        initialize_openai()
        
        # 构建消息
        messages = build_messages_description1(video_name)
        
        # 载入JSON配置文件
        with open("description_bgm_en.json", "r", encoding="utf-8") as file:
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
    video_name = "Technology-quality UI science-fiction interface program swab malfunction sound late clips of audio music"
    categories = [ "Science and technology"]

    # 调用函数
    print("Testing ask_llm function...")
    response = ask_llm_description(video_name, categories, model="gpt-4o-mini")
    print("Response from ask_llm:", response)
