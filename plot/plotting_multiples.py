import matplotlib.pyplot as plt
import numpy as np
from plot.config import get_label
from plot.utils import get_output_path


def plot_small_multiples(score_df, section):
    """
    为每个模型绘制单独的小图，以更清晰地显示分数分布

    Args:
        score_df (DataFrame): 分数数据
        section (str): 部分名称

    Returns:
        list: 表现不达标的模型列表（ROUGE和BERT分数都低于0.85的模型）
    """
    if score_df.empty:
        print(f"警告: {get_label(section)}部分没有足够的数据绘制小倍数图")
        return []

    # 获取模型列表
    models = score_df['模型'].unique()

    # 用于存储不达标的模型
    underperforming_models = []

    # 设置图形行列数
    n_models = len(models)
    n_cols = min(4, n_models)  # 最多4列
    n_rows = (n_models + n_cols - 1) // n_cols

    # 创建两个大图，每个包含所有模型的小图
    fig_rouge, axes_rouge = plt.subplots(
        n_rows, n_cols, figsize=(5*n_cols, 4*n_rows))
    fig_bert, axes_bert = plt.subplots(
        n_rows, n_cols, figsize=(5*n_cols, 4*n_rows))

    # 确保axes是二维数组
    if n_rows == 1:
        axes_rouge = axes_rouge.reshape(1, -1)
        axes_bert = axes_bert.reshape(1, -1)

    # 设置不同的颜色
    colors = plt.cm.tab10(np.linspace(0, 1, n_models))

    # x轴和y轴的范围
    x_min, x_max = score_df['总长度'].min(), score_df['总长度'].max()
    x_range = np.linspace(x_min, x_max, 100)

    # 绘制每个模型的散点图
    for idx, model in enumerate(models):
        row = idx // n_cols
        col = idx % n_cols

        model_data = score_df[score_df['模型'] == model]

        # 为当前模型选择颜色
        color = colors[idx]

        # 计算ROUGE和BERT分数的最大值
        rouge_avg = model_data['ROUGE分数'].mean(skipna=True)
        bert_avg = model_data['BERT分数'].mean(skipna=True)

        # ROUGE分数散点图
        axes_rouge[row, col].scatter(
            model_data['总长度'],
            model_data['ROUGE分数'],
            color=color,
            s=40,
            alpha=0.8
        )

        # 添加趋势线
        if len(model_data) > 1:
            z = np.polyfit(model_data['总长度'], model_data['ROUGE分数'], 1)
            p = np.poly1d(z)
            axes_rouge[row, col].plot(x_range, p(
                x_range), '-', color=color, alpha=0.6, linewidth=1.5)

        if rouge_avg < 0.5:
            underperforming_models.append(model)
            title_color = 'red'
        else:
            title_color = 'black'
            
        # 打印不达标的模型
        if underperforming_models:
            print(f"\n警告: 以下模型的ROUGE不达标")
            for model in underperforming_models:
                print(f"- {model}")
            underperforming_models = []
        # 添加警戒线

        axes_rouge[row, col].axhline(
            y=0.85, color='red', linestyle='--', linewidth=1, alpha=0.7)

        # 设置标题和范围
        axes_rouge[row, col].set_title(f"{model}\nROUGE平均: {rouge_avg:.3f}",
                                       fontsize=10, color=title_color)
        axes_rouge[row, col].set_ylim(0, 1.0)
        axes_rouge[row, col].grid(True, linestyle='--', alpha=0.3)

        # 检查是否达标（只要有一个点达到0.85就算达标）
        if bert_avg < 0.7:
            underperforming_models.append(model)
            title_color = 'red'
        else:
            title_color = 'black'
            
        # 打印不达标的模型
        if underperforming_models:
            print(f"\n警告: 以下模型的BERT分数不达标")
            for model in underperforming_models:
                print(f"- {model}")
            underperforming_models = []
        # 添加警戒线

        # BERT分数散点图
        axes_bert[row, col].scatter(
            model_data['总长度'],
            model_data['BERT分数'],
            color=color,
            s=40,
            alpha=0.8
        )

        # 添加趋势线
        if len(model_data) > 1:
            z = np.polyfit(model_data['总长度'], model_data['BERT分数'], 1)
            p = np.poly1d(z)
            axes_bert[row, col].plot(x_range, p(
                x_range), '-', color=color, alpha=0.6, linewidth=1.5)

        # 添加警戒线
        axes_bert[row, col].axhline(
            y=0.85, color='red', linestyle='--', linewidth=1, alpha=0.7)

        # 设置标题和范围
        axes_bert[row, col].set_title(f"{model}\nBERT平均: {bert_avg:.3f}",
                                      fontsize=10, color=title_color)
        axes_bert[row, col].set_ylim(0, 1.0)
        axes_bert[row, col].grid(True, linestyle='--', alpha=0.3)

    # 移除多余的子图
    for idx in range(len(models), n_rows * n_cols):
        row = idx // n_cols
        col = idx % n_cols
        fig_rouge.delaxes(axes_rouge[row, col])
        fig_bert.delaxes(axes_bert[row, col])

    # 设置总标题
    fig_rouge.suptitle(
        f"{get_label(section)} - ROUGE分数分布", fontsize=16, y=1.02)
    fig_bert.suptitle(f"{get_label(section)} - BERT分数分布", fontsize=16, y=1.02)

    # 调整布局
    fig_rouge.tight_layout()
    fig_bert.tight_layout()

    # 为所有子图添加共享的x轴和y轴标签
    fig_rouge.text(0.5, 0.02, get_label('字数'), ha='center', fontsize=12)
    fig_rouge.text(0.02, 0.5, 'ROUGE Score', va='center',
                   rotation='vertical', fontsize=12)
    fig_bert.text(0.5, 0.02, get_label('字数'), ha='center', fontsize=12)
    fig_bert.text(0.02, 0.5, 'BERT Score', va='center',
                  rotation='vertical', fontsize=12)

    # 保存图片
    rouge_output_filename = get_output_path(f"{section}_rouge_multiples.jpg")
    fig_rouge.savefig(rouge_output_filename, dpi=300, bbox_inches='tight')
    print(f"已保存ROUGE分数图到 {rouge_output_filename}")

    bert_output_filename = get_output_path(f"{section}_bert_multiples.jpg")
    fig_bert.savefig(bert_output_filename, dpi=300, bbox_inches='tight')
    print(f"已保存BERT分数图到 {bert_output_filename}")

    plt.close(fig_rouge)
    plt.close(fig_bert)


    return underperforming_models
