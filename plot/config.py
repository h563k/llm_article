import matplotlib.pyplot as plt
import matplotlib as mpl
import matplotlib.font_manager as fm

# 设置中文字体支持


# 设置中文字体支持
def configure_fonts():
    # 确保负号正常显示
    plt.rcParams['axes.unicode_minus'] = False

    # 设置全局样式
    plt.style.use('seaborn-v0_8-whitegrid')
    mpl.rcParams['axes.grid'] = True
    mpl.rcParams['grid.alpha'] = 0.3
    mpl.rcParams['grid.linestyle'] = '--'
    
    # # 强制重新加载字体
    # plt.rcParams['font.family'] = 'sans-serif'
    # plt.rcParams['font.sans-serif'] = ['WenQuanYi Micro Hei', 'SimHei']
    
    # 指定字体文件的完整路径
    font_path = '/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc'  # 替换为您的字体文件路径
    prop = fm.FontProperties(fname=font_path)

    # 设置Matplotlib默认字体
    plt.rcParams['font.family'] = prop.get_name()
    plt.rcParams['axes.unicode_minus'] = False  # 解决负号'-'显示为方块的问题

# 自定义函数：使用英文替代中文标签
def use_english_labels(use_english):
    """
    设置是否使用英文替代中文标签，避免字体问题

    Args:
        use_english (bool): 是否使用英文标签

    Returns:
        dict: 中英文标签映射字典
    """
    LABEL_MAPPING = {
        # 错误类型
        '句式错误': 'Sentence Error' if use_english else '句式错误',
        '语法错误': 'Grammar Error' if use_english else '语法错误',
        '用词不当': 'Improper Wording' if use_english else '用词不当',
        '错别字': 'Typo' if use_english else '错别字',
        '标点符号': 'Punctuation' if use_english else '标点符号',
        '重复冗余': 'Redundancy' if use_english else '重复冗余',
        '逻辑问题': 'Logic Issue' if use_english else '逻辑问题',
        '术语规范': 'Terminology' if use_english else '术语规范',

        # 部分
        '中文摘要': 'Chinese Abstract' if use_english else '中文摘要',
        '正文': 'Main Text' if use_english else '正文',
        '参考文献': 'References' if use_english else '参考文献',
        '英文部分': 'English Section' if use_english else '英文部分',

        # 图表标题和标签
        '错误率': 'Error Rate' if use_english else '错误率',
        '模型': 'Model' if use_english else '模型',
        '字数': 'Word Count' if use_english else '字数',
        '错误率箱体图': 'Error Rate Box Plot' if use_english else '错误率箱体图',
        '分布': 'Distribution' if use_english else '分布',
        '模型错误类型雷达图': 'Model Error Type Radar Chart' if use_english else '模型错误类型雷达图',
        '分数分布图': 'Score Distribution' if use_english else '分数分布图',
        '警戒线': 'Threshold' if use_english else '警戒线',
        '每个模型的分数分布': 'Score Distribution for Each Model' if use_english else '每个模型的分数分布',
        '平均': 'Avg' if use_english else '平均',

        # 组
        '组': 'Group' if use_english else '组'
    }
    return LABEL_MAPPING


# 配置
# 设置是否使用英文标签（避免中文字体问题）
# 默认使用英文标签，如果您的系统支持中文字体，可以设置为False

def get_label(key, use_english=False):
    """获取映射后的标签"""
    LABEL_MAPPING = use_english_labels(use_english)
    return LABEL_MAPPING.get(key, key)
