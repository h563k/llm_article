import matplotlib.pyplot as plt
import numpy as np
from plot.config import get_label
from plot.utils import get_output_path

def plot_scores(score_df, section):
    """
    绘制ROUGE和BERT分数散点图 (改进版)
    
    Args:
        score_df (DataFrame): 分数数据
        section (str): 部分名称
    """
    if score_df.empty:
        print(f"警告: {get_label(section)}部分没有足够的数据绘制分数图")
        return
    
    # 获取模型列表
    models = score_df['模型'].unique()
    
    # 如果模型太多，分成两个图
    max_models_per_chart = 6
    model_groups = [models[i:i+max_models_per_chart] for i in range(0, len(models), max_models_per_chart)]
    
    for group_idx, model_group in enumerate(model_groups):
        # 创建画布 (改进布局)
        fig, axes = plt.subplots(2, 1, figsize=(14, 16), dpi=100)
        
        # 设置更好的颜色和标记
        colors = plt.cm.tab10(np.linspace(0, 1, len(model_group)))
        markers = ['o', 's', '^', 'd', 'v', '*']
        
        # 用于趋势线的x范围
        x_range = np.linspace(min(score_df['总长度']), max(score_df['总长度']), 100)
        
        # 绘制ROUGE分数散点图
        for i, model in enumerate(model_group):
            model_data = score_df[score_df['模型'] == model]
            
            # 散点图 (半透明)
            axes[0].scatter(
                model_data['总长度'], 
                model_data['ROUGE分数'],
                label=model, 
                color=colors[i],
                marker=markers[i % len(markers)],
                s=70,  # 适当的点大小
                alpha=0.7,  # 半透明
                edgecolor='w',  # 白色边缘
                linewidth=0.5  # 边缘线宽度
            )
            
            # 添加趋势线
            if len(model_data) > 1:
                z = np.polyfit(model_data['总长度'], model_data['ROUGE分数'], 1)
                p = np.poly1d(z)
                axes[0].plot(x_range, p(x_range), '--', color=colors[i], alpha=0.8, linewidth=1.5)
        
        # 添加警戒线
        axes[0].axhline(y=0.85, color='red', linestyle='-', linewidth=2, 
                      label=f"{get_label('警戒线')} (0.85)", alpha=0.7)
        
        # 设置标题和标签
        group_suffix = f" ({get_label('组')} {group_idx+1})" if len(model_groups) > 1 else ""
        axes[0].set_title(f"{get_label(section)} - ROUGE {get_label('分数分布图')}{group_suffix}", fontsize=16, pad=15)
        axes[0].set_xlabel(get_label('字数'), fontsize=14)
        axes[0].set_ylabel("ROUGE Score", fontsize=14)  # 保持英文以避免字体问题
        axes[0].set_ylim(0, 1.0)
        
        # 改进网格线和背景
        axes[0].grid(True, linestyle='--', alpha=0.4)
        axes[0].set_axisbelow(True)  # 网格线在数据点后面
        
        # 改进图例位置和样式
        axes[0].legend(
            loc='upper center', 
            bbox_to_anchor=(0.5, -0.15), 
            ncol=3, 
            fontsize=12,
            frameon=True,
            framealpha=0.9,
            edgecolor='gray'
        )
        
        # 绘制BERT分数散点图
        for i, model in enumerate(model_group):
            model_data = score_df[score_df['模型'] == model]
            
            # 散点图 (半透明)
            axes[1].scatter(
                model_data['总长度'], 
                model_data['BERT分数'],
                label=model, 
                color=colors[i],
                marker=markers[i % len(markers)],
                s=70,  # 适当的点大小
                alpha=0.7,  # 半透明
                edgecolor='w',  # 白色边缘
                linewidth=0.5  # 边缘线宽度
            )
            
            # 添加趋势线
            if len(model_data) > 1:
                z = np.polyfit(model_data['总长度'], model_data['BERT分数'], 1)
                p = np.poly1d(z)
                axes[1].plot(x_range, p(x_range), '--', color=colors[i], alpha=0.8, linewidth=1.5)
        
        # 添加警戒线
        axes[1].axhline(y=0.85, color='red', linestyle='-', linewidth=2, 
                      label=f"{get_label('警戒线')} (0.85)", alpha=0.7)
        
        # 设置标题和标签
        axes[1].set_title(f"{get_label(section)} - BERT {get_label('分数分布图')}{group_suffix}", fontsize=16, pad=15)
        axes[1].set_xlabel(get_label('字数'), fontsize=14)
        axes[1].set_ylabel("BERT Score", fontsize=14)  # 保持英文以避免字体问题
        axes[1].set_ylim(0, 1.0)
        
        # 改进网格线和背景
        axes[1].grid(True, linestyle='--', alpha=0.4)
        axes[1].set_axisbelow(True)  # 网格线在数据点后面
        
        # 改进图例位置和样式
        axes[1].legend(
            loc='upper center', 
            bbox_to_anchor=(0.5, -0.15), 
            ncol=3, 
            fontsize=12,
            frameon=True,
            framealpha=0.9,
            edgecolor='gray'
        )
        
        plt.tight_layout()
        if len(model_groups) > 1:
            output_filename = get_output_path(f"{section}_scores_{group_idx+1}.jpg")
        else:
            output_filename = get_output_path(f"{section}_scores.jpg")
        plt.savefig(output_filename, dpi=300, bbox_inches='tight')
        print(f"已保存分数图到 {output_filename}")
        plt.close(fig)