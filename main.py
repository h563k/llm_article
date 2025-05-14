from functionals.data_process import DataProcess
from functionals.llm_process import summarize_llm, SingleAggregation
from functionals.multi_process import multi_process_template_model, merge_excel_files, multi_process_template_eval

if __name__ == '__main__':
    # 完整模型列表
    template_model_list = [
        ("deepseek", "deepseek-chat"),
        # 添加更多的 template 和 model 对
    ]
    # # 第一步 数据预处理
    DataProcess()
    summarize_llm()
    # # # # # 调用多进程函数
    multi_process_template_model(template_model_list, 32)
    # # # # 配置需求较高, 酌情使用
    multi_process_template_eval(template_model_list, 16)
    for template, model in template_model_list:
        SingleAggregation(template, model)
    merge_excel_files("data/result", "data/final_count")
