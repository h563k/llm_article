import os
import pandas as pd
import multiprocessing
from functionals.llm_process import SingleProcess

def merge_files(file_list):
    # 初始化一个空的DataFrame
    combined_df = pd.DataFrame()
    for filename in file_list:
        # 读取Excel文件
        df = pd.read_excel(filename)
        # 将读取的DataFrame拼接到combined_df中
        combined_df = pd.concat([combined_df, df], ignore_index=True)
    return combined_df


def merge_excel_files(directory, output_file):
    abstract = []
    content = []
    reference = []
    # 遍历目录下的所有文件
    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)
        # 检查文件是否是Excel文件
        if filename.endswith('content.xlsx'):
            content.append(file_path)
        elif filename.endswith('reference.xlsx'):
            reference.append(file_path)
        elif filename.endswith('abstract.xlsx'):
            abstract.append(file_path)
    reference = merge_files(reference)
    abstract = merge_files(abstract)
    content = merge_files(content)
    reference.to_excel(f"{output_file}/reference.xlsx", index=False)
    abstract.to_excel(f"{output_file}/abstract.xlsx", index=False)
    content.to_excel(f"{output_file}/content.xlsx", index=False)
def process_task(template_model):
    template, model = template_model
    # 在进程内部初始化 SingleProcess
    SingleProcess(template, model)


def multi_process_template_model(template_model_list, num_processes=None):
    if num_processes is None:
        num_processes = multiprocessing.cpu_count()

    with multiprocessing.Pool(processes=num_processes) as pool:
        pool.map(process_task, template_model_list)

    



