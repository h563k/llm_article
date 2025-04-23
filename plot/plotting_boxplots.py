import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter  # 新增导入
import seaborn as sns
from plot.config import get_label
from plot.utils import get_output_path


def plot_boxplots(error_df, error_types, section, model_list):
    """
    绘制错误率箱体图 (改进版)

    Args:
        error_df (DataFrame): 错误率数据
        error_types (list): 错误类型列表
        section (str): 部分名称
    """
    if error_df.empty or not error_types:
        print(f"警告: {get_label(section)}部分没有足够的数据绘制箱体图")
        return
    print(f"绘制{get_label(section)}部分的箱体图...")
    groups = [model_list[i:i+4] for i in range(0, len(model_list), 4)]
    for group_num, model_group in enumerate(groups, 1):
        print(f"模型分组: {model_group}")
        group_df = error_df[error_df['模型'].isin(model_group)]
        # 为每种错误类型创建一个子图
        fig, axes = plt.subplots(
            len(error_types), 1, figsize=(14, 4 * len(error_types)))
        if len(error_types) == 1:
            axes = [axes]

        # 设置自定义配色方案
        palette = sns.color_palette(
            "viridis", n_colors=len(model_group))  # 按当前分组模型数量生成

        for i, error_type in enumerate(error_types):
            # 筛选当前错误类型的数据
            df_current = group_df[group_df['错误类型'] == error_type]
            # 在绘制前添加排序代码（示例）
            df_current = df_current.sort_values(
                '模型', ascending=False)  # 根据实际需求调整排序
            if df_current.empty:
                axes[i].text(0.5, 0.5, f"No data for {get_label(error_type)}",
                             horizontalalignment='center', verticalalignment='center')
                continue

            # 去掉异常值，主要是明显过大的部分
            upper_bound = df_current['错误率'].quantile(0.9)
            df_current = df_current[(df_current['错误率'] <= upper_bound)]

            # 绘制箱体图 (更美观) - 修复警告：使用hue参数而不是直接传递palette
            sns.boxplot(
                x='错误率',
                y='模型',
                hue='模型',  # 添加hue参数
                data=df_current,
                ax=axes[i],
                palette=palette,
                width=0.6,
                fliersize=3,  # 减小异常值的点大小
                linewidth=1.5,  # 增加箱体线条粗细
                legend=False,  # 不显示图例，因为我们只想用模型名称作为y轴标签
                whis=1.0,  # 缩小异常值判定范围，默认是1.5
                showfliers=False,  # 新增参数，关闭异常值显示
                boxprops={'alpha': 0.5},  # 新增透明度设置 (0-1之间调整)
                zorder=2  # 设置箱体在底层
            )
            sns.stripplot(
                x='错误率',
                y='模型',
                hue='模型',  # 添加hue参数
                data=df_current,
                ax=axes[i],
                size=6,  # 减小点大小
                alpha=0.9,  # 增加透明度
                palette='dark:peru',
                marker='o',  # 空心圆圈
                edgecolor='peru',  # 边框颜色
                jitter=0.05,  # 仅水平抖动
                dodge=False,  # 与箱体分开显示
                legend=False,  # 不显示图例，避免重复
                zorder=3  # 设置散点在顶层
            )

            # 设置标题和标签
            axes[i].set_title(
                f"{get_label(section)} - {get_label(error_type)} {get_label('分布')}", fontsize=14, pad=15)
            axes[i].set_xlabel(get_label('错误率'), fontsize=12)
            axes[i].set_ylabel(get_label('模型'), fontsize=12)
            if section == '正文':
                axes[i].xaxis.set_major_formatter(
                    FuncFormatter(lambda x, _: f'{x*10000:.1f}‱'))
            else:
                axes[i].xaxis.set_major_formatter(
                    FuncFormatter(lambda x, _: f'{x*1000:.1f}‰'))

            # 改进网格线
            axes[i].grid(axis='x', linestyle='--', alpha=0.7)
            axes[i].grid(axis='y', alpha=0)

            # 设置x轴范围，确保从0开始
            max_error = df_current['错误率'].max()
            # 正确的设置顺序（在所有绘图操作之后设置）
            # 先绘制所有元素...
            # 最后设置坐标范围
            axes[i].set_xlim(left=0, right=max_error * 1.05)  # 显式指定参数
            # axes[i].autoscale_view(scalex=False)  # 关闭自动缩放
            # 添加平均值文本
            for j, model in enumerate(df_current['模型'].unique()):
                model_mean = df_current[df_current['模型']
                                        == model]['错误率'].mean()
                axes[i].text(
                    max_error * 1.02,  # 放在图表右侧
                    j,  # y坐标位置
                    f"{get_label('平均')}: {model_mean:.5f}",
                    va='center',
                    fontsize=10
                )

        plt.tight_layout()
        output_filename = get_output_path(f"{section}_boxplots{group_num}.jpg")
        plt.savefig(output_filename, dpi=300, bbox_inches='tight')
        print(f"已保存箱体图到 {output_filename}")
        plt.close(fig)
