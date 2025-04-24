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

@retry(wait=wait_random_exponential(min=1, max=60), stop=stop_after_attempt(0))
@log_to_file
def openai_chat(system_prompt, prompt, openai_template, model):
    if config.OpenAI.get('proxy'):
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
