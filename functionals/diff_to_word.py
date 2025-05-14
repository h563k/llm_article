import difflib
import os
from docx import Document
from docx.shared import RGBColor, Pt
from docx.oxml.shared import qn
from functionals.system_config import ModelConfig
import re


def split_paragraphs(text):
    return [p.strip() for p in text.split('\n') if p.strip()]


def set_run_font(run):
    """统一设置字体格式：中文宋体，英文Times New Roman，五号字"""
    run.font.name = 'Times New Roman'  # 设置西文字体
    run._element.rPr.rFonts.set(qn('w:eastAsia'), 'SimSun')  # 设置中文字体
    run.font.size = Pt(12)  # 五号字


def apply_diff_with_format(para1, para2, doc_paragraph):
    pattern = re.compile(r'(<[^>]+>)|([^<]+)')
    tokens1 = pattern.findall(para1)
    tokens2 = pattern.findall(para2)

    text1 = ''.join([t[1] for t in tokens1 if t[1]])
    text2 = ''.join([t[1] for t in tokens2 if t[1]])
    matcher = difflib.SequenceMatcher(None, text1, text2)

    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag in ('replace', 'delete'):
            run = doc_paragraph.add_run(text1[i1:i2])
            run.font.color.rgb = RGBColor(255, 0, 0)
            run.font.strike = True
            set_run_font(run)
        if tag in ('replace', 'insert'):
            run = doc_paragraph.add_run(text2[j1:j2])
            run.font.color.rgb = RGBColor(0, 255, 0)
            set_run_font(run)
        if tag == 'equal':
            run = doc_paragraph.add_run(text1[i1:i2])
            set_run_font(run)


def word_diff(text1, text2, doc):
    paras1 = split_paragraphs(text1)
    paras2 = split_paragraphs(text2)

    for p1, p2 in zip(paras1, paras2):
        para_original = doc.add_paragraph()
        apply_diff_with_format(p1, p2, para_original)


def create_word(text_list, file_name):
    config = ModelConfig()
    file_path = config.file_path

    doc = Document()
    # 设置文档默认字体（作为备用方案）
    doc.styles['Normal'].font.name = 'Times New Roman'
    doc.styles['Normal']._element.rPr.rFonts.set(qn('w:eastAsia'), 'SimSun')

    doc.add_heading(f'{file_name}文本比较版', 0)

    for text1, text2 in text_list:
        word_diff(text1, text2, doc)

    save_path = os.path.join(file_path, 'data', 'word_diff', file_name)
    doc.save(save_path)
