from functionals.data_process import DataProcess
from functionals.llm_process import summarize_llm, SingleCount
from functionals.multi_process import multi_process_template_model, merge_excel_files

if __name__ == '__main__':
    # 完整模型列表
    template_model_list = [
        ("yi", "yi-large"),
        ("qwen", "deepseek-v3"),
        ("qwen", "deepseek-r1"),
        ("qwen", "qwq-32b-preview"),
        ("qwen", "qwen2.5-72b-instruct"),
        ("kimi", "moonshot-v1-auto"),
        ("chatglm", "GLM-4-Air-0111"),
        ("baidu", "ernie-3.5-128k"),
        ("doubao", "doubao-1-5-pro-32k-250115"),
        ("openai_wild", "gpt-3.5-turbo"),
        ("openai_wild", "gpt-4o-mini"),
        # 添加更多的 template 和 model 对
    ]
    # 第一步 数据预处理
    # DataProcess()
    # summarize_llm()
    # # 调用多进程函数
    # multi_process_template_model(template_model_list, 32)
    for template, model in template_model_list:
        SingleCount(template, model)
    merge_excel_files("data/result", "data/final_count")
