import os
import openai
# from langchain_openai import ChatOpenAI
# from langchain.schema import SystemMessage  # 这里修正了导入路径
# from langchain.memory import ConversationBufferMemory
# from langchain.chains.conversation.base import ConversationChain
# from autogen import ConversableAgent, initiate_chats
from tenacity import (
    retry,
    stop_after_attempt,
    wait_random_exponential,
)  # for exponential backoff
from functionals.system_config import ModelConfig
from functionals.standard_log import log_to_file

config = ModelConfig()
openai_config = config.OpenAI


def env_init() -> None:
    os.environ['http_proxy'] = config.OpenAI['proxy']
    os.environ['https_proxy'] = config.OpenAI['proxy']
    os.environ['ftp_proxy'] = config.OpenAI['proxy']
    os.environ['no_proxy'] = '127.0.0.1,localhost'
    os.environ['HTTP_PROXY'] = config.OpenAI['proxy']
    os.environ['HTTPS_PROXY'] = config.OpenAI['proxy']
    os.environ['FTP_PROXY'] = config.OpenAI['proxy']
    os.environ['NO_PROXY'] = '127.0.0.1,localhost'


# class ArticleLLM:
#     def __init__(self, system_prompt, name, openai_template, model, cache_seed=None) -> None:
#         self.openai_template = openai_template
#         self.llm_config = self.llm_env_init(model, openai_template, cache_seed)
#         self.agent = self.create_agent(system_prompt, name)
#         self.user_proxy = self.user_input()
#
#     def llm_env_init(self, model, openai_template, cache_seed):
#         env_init()
#         api_key = openai_config[openai_template]['api_key']
#         base_url = openai_config[openai_template]['base_url']
#         config_list = [
#             {
#                 "model": model,
#                 "api_key": api_key,
#                 "api_type": "openai",
#                 "base_url": base_url,
#                 "temperature": openai_config['temperature'],
#                 "price": [0, 0],
#             }
#         ]
#         llm_config = {"config_list": config_list,
#                       "cache_seed": cache_seed,
#                       }
#         return llm_config
#
#     def user_input(self):
#         user_proxy = ConversableAgent(
#             name="MessageForwarderAgent",
#             system_message="You are a message forwarder, and your task is to forward the received messages unaltered to the next recipient.",
#             llm_config=False,  # 不使用LLM生成回复
#             code_execution_config=False,  # 禁用代码执行
#             human_input_mode="NEVER",  # 不请求人工输入
#         )
#         return user_proxy
#
#     def create_agent(self, system_prompt, name):
#         agent = ConversableAgent(
#             name=name,
#             llm_config=self.llm_config,
#             human_input_mode="NEVER",  # always
#             system_message=system_prompt,
#         )
#         return agent
#
#     @retry(wait=wait_random_exponential(min=1, max=60), stop=stop_after_attempt(0))
#     @log_to_file
#     def chat(self, prompt_list):
#         chats = []
#         for prompt in prompt_list:
#             chat_content = {"sender": self.user_proxy,
#                             "recipient": self.agent,
#                             "message": prompt,
#                             "max_turns": 1,
#                             "clear_history": False
#                             }
#             chats.append(chat_content)
#         chat_results = initiate_chats(chats)
#         return chat_results


# @retry(wait=wait_random_exponential(min=1, max=60), stop=stop_after_attempt(0))
# @log_to_file
# def langchain_chat(system_prompt, prompt_list, openai_template, model):
#     env_init()
#     api_key = openai_config[openai_template]['api_key']
#     base_url = openai_config[openai_template]['base_url']
#
#     # 创建一个系统消息来传递给模型
#     system_message = SystemMessage(content=system_prompt)
#
#     # 初始化模型和记忆
#     memory = ConversationBufferMemory(
#         memory_key="history", return_messages=True)
#
#     # 你可以选择配置OpenAI的Chat模型
#     chat_model = ChatOpenAI(
#         model=model,
#         temperature=openai_config['temperature'],
#         api_key=api_key,
#         base_url=base_url)
#
#     # 创建对话链，将system_message作为系统输入传递
#     conversation = ConversationChain(
#         llm=chat_model,
#         memory=memory,
#         verbose=True,  # 如果需要查看对话详情，可以开启verbose
#     )
#
#     # 首次对话时，把系统消息作为上下文传递
#     conversation.memory.chat_memory.add_message(system_message)
#     response_list = []
#     # 开始对话
#     for prompt in prompt_list:
#         response = conversation.predict(input=prompt)
#         print(response)
#         response_list.append(response)
#     return response_list


@retry(wait=wait_random_exponential(min=1, max=60), stop=stop_after_attempt(0))
@log_to_file
def openai_chat(system_prompt, prompt, openai_template, model):
    env_init()
    api_key = openai_config[openai_template]['api_key']
    base_url = openai_config[openai_template]['base_url']
    client = openai.OpenAI(api_key=api_key, base_url=base_url)
    response = client.chat.completions.create(
        model=model,
        temperature=openai_config['temperature'],
        presence_penalty=openai_config['presence_penalty'],
        frequency_penalty=openai_config['frequency_penalty'],
        stream=True,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ],
    )
    full_response = ""
    for chunk in response:
        delta = chunk.choices[0].delta.content
        full_response += str(delta)
    full_response = full_response.strip('None')
    return full_response
