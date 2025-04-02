import pandas as pd
from functionals.system_config import ModelConfig


def load_data():
    """
    读取数据文件并进行预处理

    Returns:
        dict: 包含各部分数据的字典
    """
    config = ModelConfig()
    file_path = config.file_path
    # 读取摘要数据
    abstract_df = pd.read_excel(f'{file_path}/data/final_count/abstract.xlsx')

    # 读取正文数据
    content_df = pd.read_excel(f'{file_path}/data/final_count/content.xlsx')
    
    # 读取参考文献数据
    reference_df = pd.read_excel(
        f'{file_path}/data/final_count/reference.xlsx')
    
    # 假设content_df已加载
    chinese_abstract_df = content_df[content_df['统计类型'] == '中文摘要']
    content_df = content_df[content_df['统计类型'] == '正文']
    # 返回处理后的数据
    return {
        '英文摘要': abstract_df,
        '中文摘要': chinese_abstract_df,
        '正文': content_df,
        '参考文献': reference_df
    }


def get_error_columns(section):
    assert section in ['英文摘要', '正文', '参考文献', '中文摘要'], "section参数必须是英文摘要、正文或参考文献"
    # 错误类型列表 (基于示例数据中的列名)
    if section == '英文摘要':
        error_columns = ['句式错误', '语法错误', '拼写词汇错误',
                         '术语使用错误', '格式规范错误', '数字单位错误', '空格使用错误']
    elif section == '中文摘要':
        error_columns = ['句式错误', '语法错误', '用词不当',
                         '错别字', '标点符号', '重复冗余', '逻辑问题', '术语规范']
    elif section == '正文':
        error_columns = ['句式错误', '语法错误', '用词不当',
                         '错别字', '标点符号', '重复冗余', '逻辑问题', '术语规范']
    elif section == '参考文献':
        error_columns = ['作者信息错误或不规范', '期刊或书籍名称格式问题', '文献类型混淆', '出版年与其他细节不一致',
                         'DOI与其他信息遗漏或错误', '参考文献顺序错误', '中文和英文标点符号混用', '重复引用与排版问题', '页码与文章编号问题']
    return error_columns


def prepare_error_data(df, section):
    """
    根据原始数据准备用于绘图的错误率数据

    Args:
        df (DataFrame): 原始数据
        section (str): 部分名称

    Returns:
        tuple: (错误率数据DataFrame, 可用的错误类型列表)
    """

    # 模型列表
    models = df['模型'].unique()
    error_columns = get_error_columns(section)

    # 为每个模型、每种错误类型计算错误率
    data = []
    for model in models:
        model_data = df[df['模型'] == model]

        for error_type in error_columns:
            # 检查错误类型是否在DataFrame中
            if error_type in df.columns:
                for _, row in model_data.iterrows():
                    # 计算错误率 (错误数 / 总长度)
                    if row['总长度'] > 0:  # 避免除以零
                        error_rate = row[error_type] / row['总长度']
                    else:
                        error_rate = 0

                    data.append({
                        '模型': model,
                        '错误类型': error_type,
                        '文件名': row['文件名'],
                        '错误率': error_rate,
                        '总长度': row['总长度']
                    })

    # 转换为DataFrame
    error_df = pd.DataFrame(data)

    # 获取该部分所有可用的错误类型
    available_error_types = [et for et in error_columns if et in df.columns]

    return error_df, available_error_types


def prepare_radar_data(df, section):
    """
    根据原始数据准备用于雷达图的数据

    Args:
        df (DataFrame): 原始数据
        section (str): 部分名称

    Returns:
        tuple: (雷达图数据DataFrame, 可用的错误类型列表)
    """
    # 错误类型列表
    error_columns = get_error_columns(section)

    # 模型列表
    models = df['模型'].unique()

    # 为每个模型计算每种错误类型的平均错误率
    data = {}
    for model in models:
        model_data = df[df['模型'] == model]
        model_errors = {}

        for error_type in error_columns:
            # 检查错误类型是否在DataFrame中
            if error_type in df.columns:
                # 计算平均错误率
                total_errors = model_data[error_type].sum()
                total_length = model_data['总长度'].sum()

                if total_length > 0:  # 避免除以零
                    avg_error_rate = total_errors / total_length
                else:
                    avg_error_rate = 0

                model_errors[error_type] = avg_error_rate

        data[model] = model_errors

    # 转换为DataFrame
    radar_df = pd.DataFrame(data)

    # 获取该部分所有可用的错误类型
    available_error_types = [et for et in error_columns if et in df.columns]

    return radar_df, available_error_types


def prepare_score_data(df, section):
    """
    根据原始数据准备用于分数散点图的数据

    Args:
        df (DataFrame): 原始数据
        section (str): 部分名称

    Returns:
        DataFrame: 分数数据
    """
    # 确保分数列存在
    if 'rougel' not in df.columns or 'bert_score' not in df.columns:
        print(f"警告: {get_label(section)}部分缺少分数列")
        return pd.DataFrame()

    # 提取需要的列
    score_df = df[['文件名', '模型', '总长度', 'rougel', 'bert_score']].copy()

    # 重命名列以匹配后续函数
    score_df.rename(columns={
        'rougel': 'ROUGE分数',
        'bert_score': 'BERT分数'
    }, inplace=True)

    return score_df
