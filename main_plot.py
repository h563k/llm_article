"""
模型比较可视化主程序
用于绘制箱体图、雷达图、分数散点图和小倍数图，以比较不同语言模型的性能
"""

from plot.config import configure_fonts
from plot.data_processing import load_data, prepare_error_data, prepare_radar_data, prepare_score_data
from plot.plotting_boxplots import plot_boxplots
from plot.plotting_radar import plot_radar
from plot.plotting_scores import plot_scores
from plot.plotting_multiples import plot_small_multiples
from plot.utils import ensure_output_dir, output_clean

model_list = ['gpt-3.5-turbo',
              'yi-large',
              'GLM-4-Air-0111',
              'ernie-3.5-128k',
              'moonshot-v1-auto',
              'qwen2.5-72b-instruct',
              'doubao-1-5-pro-32k-250115',
              'gpt-4o-2024-08-06',
              'gpt-4o-mini',
              'deepseek-v3',
              'deepseek-r1',
              'qwq-32b-preview',]


def plot_all_charts(model_list):
    """
    为所有部分绘制所有图表
    """
    print("开始读取数据文件...")

    try:
        # 配置字体
        configure_fonts()

        # 确保输出目录存在
        output_dir = ensure_output_dir()
        output_clean()
        print(f"图表将保存到目录: {output_dir}")

        # 读取数据
        data_dict = load_data()

        # 部分名称列表
        sections = list(data_dict.keys())

        for section in sections:
            print(f"处理{section}部分的数据...")
            df = data_dict[section]

            if df is None or df.empty:
                print(f"警告: {section}部分没有数据")
                continue

            print(f"准备{section}部分的错误率数据...")
            error_df, error_types = prepare_error_data(df, section)

            print(f"准备{section}部分的雷达图数据...")
            radar_df, radar_error_types = prepare_radar_data(df, section)
            # print(f"雷达图数据准备完成，包含错误类型: {radar_df}")

            print(f"准备{section}部分的分数数据...")
            score_df = prepare_score_data(df, section)

            print(f"绘制{section}部分的箱体图...")
            # plot_boxplots(error_df, error_types, section, model_list)

            print(f"绘制{section}部分的雷达图...")
            plot_radar(radar_df, radar_error_types, section, model_list)

            # print(f"绘制{section}部分的分数散点图...")
            # plot_scores(score_df, section, model_list)

            # print(f"绘制{section}部分的小倍数图...")
            # plot_small_multiples(score_df, section, model_list)

            # print(f"{section}部分的图表已生成完毕")

        print(f"所有图表绘制完成！请在 {output_dir} 目录中查看")

    except Exception as e:
        print(f"错误: {str(e)}")
        import traceback
        traceback.print_exc()


# 主函数
if __name__ == "__main__":
    # 绘制所有图表
    plot_all_charts(model_list)
