import matplotlib.pyplot as plt
from matplotlib.ticker import FormatStrFormatter
import numpy as np
from plot.config import get_label
from plot.utils import get_output_path


def plot_radar(radar_df, error_types, section,  model_list, exclude_models=None,):
    log_base = 10  # 对数基数
    """
    绘制错误类型雷达图 (改进版)
    
    Args:
        radar_df (DataFrame): 雷达图数据
        error_types (list): 错误类型列表
        section (str): 部分名称
        exclude_models (list, optional): 要排除的模型列表
    """
    if radar_df.empty or not error_types:
        print(f"警告: {get_label(section)}部分没有足够的数据绘制雷达图")
        return

    # 过滤掉不达标的模型
    if exclude_models:
        radar_df = radar_df.drop(columns=exclude_models)
        print(f"已从雷达图中排除以下不达标模型: {', '.join(exclude_models)}")

    models = radar_df.columns.tolist()
    if not models:
        print(f"警告: 过滤后没有剩余的模型可供绘制雷达图")
        return

    # 准备雷达图数据
    num_error_types = len(error_types)
    angles = np.linspace(0, 2 * np.pi, num_error_types,
                         endpoint=False).tolist()
    angles += angles[:1]  # 闭合图形

    # 创建极坐标子图
    fig, ax = plt.subplots(figsize=(10, 10), subplot_kw=dict(polar=True))

    # 使用 tab10 调色板，获取适量的颜色
    colors = plt.cm.tab10(np.linspace(0, 1, len(models)))

    # 找到最小的非零值，用于处理0值
    min_nonzero = radar_df[radar_df > 0].min().min()
    # 动态确定y轴范围
    min_value = np.log(min_nonzero/10)/np.log(log_base)  # "将0值替换为最小非零值的1/10"
    # 绘制每个模型的雷达图
    for i, model in enumerate(models):
        values = radar_df[model].values.tolist()
        # 对数据进行对数转换，将0值替换为最小非零值的1/10
        values = [min_value if v == 0 else np.log(
            v)/np.log(log_base) for v in values]
        values += values[:1]  # 闭合图形
        ax.plot(angles, values, color=colors[i], linewidth=2.5, label=model)
        ax.fill(angles, values, color=colors[i], alpha=0.15)

    # 设置错误类型标签（转换为可读标签）
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels([get_label(et) for et in error_types], fontsize=11)

    # 动态确定最大值
    print('max_value')
    print(np.log(radar_df[models].max().max())/np.log(log_base))
    max_value = np.ceil(np.log(radar_df[models].max().max())/np.log(log_base))
    ax.set_ylim(min_value, max_value)

    # Y 轴刻度
    yticks = np.arange(min_value, max_value + 1)
    ax.set_yticks(yticks)
    # 将刻度值转换回原始尺度（科学计数法）
    ax.set_yticklabels([f'{log_base}^{int(x)}' for x in yticks], fontsize=10)

    # 优化网格线
    ax.grid(linewidth=0.8, alpha=0.3)

    # 添加图例（移到图表外部）
    ax.legend(loc='upper center', bbox_to_anchor=(
        0.5, -0.05), ncol=3, fontsize=11)

    # 设置标题
    plt.title(
        f"{get_label(section)} - {get_label('模型错误类型雷达图')} (log10尺度)", size=15, y=1.08)

    # 调整布局并保存结果
    plt.tight_layout()
    output_filename = get_output_path(f"{section}_radar.jpg")
    plt.savefig(output_filename, dpi=300, bbox_inches='tight')
    print(f"已保存雷达图到 {output_filename}")

    # 关闭图像，释放内存
    plt.close(fig)
