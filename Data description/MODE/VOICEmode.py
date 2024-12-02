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
def build_messages_description(role_name, gender, age, language, description, style, field):
    with open("description_voice_en.json", "r", encoding="utf-8") as file:
        config = json.load(file)
    
    system_prompt = config["systemPrompt"]
    messages = [{"role": "system", "content": system_prompt}]
    
    
    messages.append({"role": "user", "content": f"名字: {role_name}"})
    messages.append({"role": "user", "content": f"性别: {gender}"})
    messages.append({"role": "user", "content": f"年龄: {age}"})
    messages.append({"role": "user", "content": f"语种: {language}"})
    messages.append({"role": "user", "content": f"音色描述: {description}"})
    messages.append({"role": "user", "content": f"风格关键词: {style}"})
    messages.append({"role": "user", "content": f"领域关键词: {field}"})
    return messages

# 请求处理
def ask_llm_description(role_name, gender, age, language, description, style, field, model="gpt-4o-mini"):
    try:
        # 初始化OpenAI配置
        initialize_openai()
        
        # 构建消息
        messages = build_messages_description(role_name, gender, age, language, description, style, field)
        
        # 载入JSON配置文件
        with open("description_voice_en.json", "r", encoding="utf-8") as file:
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
    role_name="贝儿"
    gender="women"
    age="Youth"
    language="Chinese-Taiwan"
    description="Entertainment. It's natural."
    style="Calm down."
    field="Information, celebrity, entertainment"
    # 调用函数
    print("Testing ask_llm function...")
    response = ask_llm_description(role_name, gender, age, language, description, style, field, model="gpt-4o-mini")
    print("Response from ask_llm:", response)
