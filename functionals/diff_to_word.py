import difflib
import os
from docx import Document
from docx.shared import RGBColor
from functionals.system_config import ModelConfig


def word_diff(text1, text2, doc):
    # 去除空行和多余的空格，确保文本是连贯的
    text1 = ' '.join(text1.split())
    text2 = ' '.join(text2.split())

    # 使用 difflib.SequenceMatcher 进行精确的差异对比
    matcher = difflib.SequenceMatcher(None, text1, text2)
    diff = matcher.get_opcodes()
    
    para = doc.add_paragraph()
    # 处理差异，生成连贯的文本
    for tag, i1, i2, j1, j2 in diff:
        before_subtext = text1[i1:i2]
        after_subtext = text2[j1:j2]

        if tag == 'replace' or tag == 'delete':  # 如果是替换或删除
            # 删除的部分：红色 + 删除线
            run = para.add_run(before_subtext)
            run.font.color.rgb = RGBColor(255, 0, 0)  # 红色
            run.font.strike = True  # 删除线

        if tag == 'replace' or tag == 'insert':  # 如果是替换或插入
            # 新增的部分：绿色
            run = para.add_run(after_subtext)
            run.font.color.rgb = RGBColor(0, 255, 0)  # 绿色

        # 对比过的内容保留不变，直接加回去
        if tag == 'equal':  # 如果是相同的部分
            run = para.add_run(before_subtext)  # 保持原文


def create_word(text_list, file_name):
    config = ModelConfig()
    file_path = config.file_path
    print(file_path)
    # 创建 Word 文档
    doc = Document()

    # 标题
    doc.add_heading(f'{file_name}文本比较版', 0)

    for text1, text2 in text_list:
        word_diff(text1, text2, doc)
    save_path = os.path.join(file_path, 'data', 'word_diff', file_name)

    doc.save(save_path)
