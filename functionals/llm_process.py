import re
import os
from fuzzywuzzy import fuzz
import pandas as pd
from functionals.save_data import DatabaseManager
from functionals.llm_api import openai_chat
from functionals.metric import eval
from functionals.file_list import get_file_list
from functionals.promot_template import *

# TODO增加一个全文英文提取promot


def summarize_llm():
    # 第二步总结大模型， 总结大模型可以交给固定模型去实现， 比如deepseek
    openai_template = 'qwen'
    model = 'deepseek-v3'
    database_manager = DatabaseManager()
    file_list = get_file_list()
    for file_name in file_list:
        if database_manager.get_summarize(file_name):
            print(f'{file_name}已存在, 跳过总结')
            continue
        content = database_manager.get_document(
            file_name=file_name, content_type="FullContent")
        content = content[0][3]
        print(f'正在总结{file_name}')
        response = openai_chat(
            system_prompt=summarize_promot,
            prompt=content,
            openai_template=openai_template,
            model=model,
        )
        response = response.strip('None')
        database_manager.save_summarize(file_name, response)


def abstract_llm(openai_template, model, file_name, system_prompt_abstract, summary, Abstract_type, database_manager):
    # task1 摘要总结
    abstract = database_manager.get_document(file_name, Abstract_type)[0][3]
    system_prompt = f"""{system_prompt_abstract}\n{summary}"""
    if not database_manager.get_reference_cache(file_name, openai_template, model, Abstract_type):
        response = openai_chat(
            system_prompt,
            prompt=abstract,
            openai_template=openai_template,
            model=model,
        )
        database_manager.save_reference_cache(
            file_name, openai_template, model, Abstract_type, abstract, response)
    else:
        print(f'{file_name}摘要润色已存在')


# 逐步的润色每一段文本
def refine_llm(openai_template, model, database_manager, file_list):
    print(f'大模型润色工具开始, 本次采用模型为{model}')
    for file_name in file_list:
        # 先获取文章的摘要
        summary = database_manager.get_summarize(file_name)[2]
        print(f'正在总结{file_name}的中文摘要')
        abstract_llm(openai_template, model, file_name,
                     system_prompt_abstract_chinese, summary, 'Abstract_Chinese', database_manager)
        print(f'正在总结{file_name}的英文摘要')
        abstract_llm(openai_template, model, file_name,
                     system_prompt_abstract_english, summary, 'Abstract_English', database_manager)
        content_list = database_manager.get_document(
            file_name=file_name, content_type="Content")
        # 正文润色
        for i, content in enumerate(content_list):
            content = content[3]
            content_tpye = f'Content{i}'
            if not database_manager.get_reference_cache(file_name, openai_template, model, content_tpye):
                print(f'{model}正在润色{file_name}的第{i}段内容')
                if re.search('(<h\d+>\d+\x20*结论.*?</h\d+>.*?)参考文献', content, re.S):
                    system_prompt = f"""{system_prompt_content_conclusion}\n{summary}"""
                else:
                    system_prompt = f"""{system_prompt_content}\n{summary}"""
                # 这里做一个简单的过滤, 过短的文本不处理
                if len(content) > 20:
                    response = openai_chat(
                        system_prompt,
                        prompt=content,
                        openai_template=openai_template,
                        model=model,
                    )
                else:
                    response = content
                database_manager.save_reference_cache(
                    file_name, openai_template, model, content_tpye, content, response)
            else:
                print(f'{file_name}的第{i}段内容已经润色')
        system_prompt = system_prompt_reference
        reference = database_manager.get_document(
            file_name=file_name, content_type="Reference")[0][3]
        print(f'{model}正在润色{file_name}的参考文献')
        # 参考文献过长需要进行分批次输入
        reference_input_list = []
        reference_list = reference.split('\n')
        temp = []
        cut_off = 0
        for reference_item in reference_list:
            cut_off += len(reference_item)
            temp.append(reference_item)
            if cut_off > 2000:
                reference_input_list.append('\n'.join(temp))
                temp = []
                cut_off = 0
        if temp:
            reference_input_list.append('\n'.join(temp))
        for i, reference in enumerate(reference_input_list):
            content_tpye = f'Reference{i}'
            if not database_manager.get_reference_cache(file_name, openai_template, model, content_tpye):
                print(f'正在润色{file_name}的第{i}段参考文献')
                response = openai_chat(
                    system_prompt,
                    prompt=reference,
                    openai_template=openai_template,
                    model=model,
                )
                database_manager.save_reference_cache(
                    file_name, openai_template, model, content_tpye, reference, response)
            else:
                print(f'{file_name}的第{i}段参考文献已经润色')
#  记录评价指标


def eval_llm(openai_template, model, database_manager, file_list):
    for file_name in file_list:
        sql = f"select * from reference_cache where file_name = '{file_name}' and template = '{openai_template}' and model = '{model}' order by id"
        reference_cache = database_manager.custom(sql)
        for i, reference_cache_item in enumerate(reference_cache):
            _, file_name, template, model, content_tpye, content, reference, _ = reference_cache_item
            print(f'{file_name}的第{i}段内容已开始评价,模型为{model},类型为{content_tpye}')
            if not database_manager.get_eval_count(file_name, openai_template, model, content_tpye):
                if len(reference) > 20:
                    eval_scores = eval(reference, content)
                else:
                    eval_scores = {'rouge_l': 1, 'bert_score': 1}
                database_manager.save_eval_count(
                    file_name, openai_template, model, content_tpye, eval_scores['rouge_l'], eval_scores['bert_score'])
            else:
                print(f'{file_name}的第{i}段内容已经评价')


def abstract_count(file_name, openai_template, model, abstract_type, system_prompt_compare, database_manager):
    # 先获取文章的摘要
    abstract = database_manager.get_reference_cache(
        file_name, openai_template, model, abstract_type)
    # 统计摘要内容
    prormt = f"""## 原文
{abstract[0][5]}
## 润色后内容
{abstract[0][6]}"""
    if not database_manager.get_compare_count(file_name, openai_template, model, abstract_type):
        print(f'正在统计{file_name}的摘要')
        response = openai_chat(
            system_prompt_compare,
            prompt=prormt,
            openai_template=openai_template,
            model=model,
        )
        database_manager.save_compare_count(
            file_name, openai_template, model, abstract_type, response)
    else:
        print(f'{file_name}的摘要已经统计')


# 创建对比函数
def compare_llm(openai_template, model, database_manager, file_list):
    print('开始统计润色结果')
    for file_name in file_list:
        abstract_count(file_name, openai_template, model,
                       'Abstract_Chinese', system_prompt_compare_chinese, database_manager)
        abstract_count(file_name, openai_template, model,
                       'Abstract_English', system_prompt_compare_english, database_manager)
        # 获取文章正文
        sql = f"""select *
from reference_cache
where content_tpye like 'Content%'
and model = '{model}' and file_name = '{file_name}' order by id"""
        content_list = database_manager.custom(sql)
        for i, content in enumerate(content_list):
            content =content[6]
            if len(content) < 20:
                print(f'{file_name}的第{i}段长度过短, 跳过处理')
                continue
            if not database_manager.get_compare_count(file_name, openai_template, model, f'Content{i}'):
                prormt = f"""## 原文
{content[5]}
## 润色后内容
{content[6]}"""
                print(f'{openai_template}正在统计{file_name}的第{i}段内容')
                response = openai_chat(
                    system_prompt_compare_chinese,
                    prompt=prormt,
                    openai_template=openai_template,
                    model=model,
                )
                database_manager.save_compare_count(
                    file_name, openai_template, model, f'Content{i}', response)
            else:
                print(f'{file_name}的第{i}段内容已经统计')

        # 获取文章参考文献
        sql = f"""select *
from reference_cache
where content_tpye like 'Reference%'
and model = '{model}' and file_name = '{file_name}' order by id"""
        reference_list = database_manager.custom(sql)
        for i, reference in enumerate(reference_list):
            if not database_manager.get_compare_count(file_name, openai_template, model, f'Reference{i}'):
                prormt = f"""## 参考文献
{reference[5]}
## 润色后内容
{reference[6]}"""
                print(f'{openai_template}正在统计{file_name}的第{i}段参考文献')
                response = openai_chat(
                    system_prompt_compare_reference,
                    prompt=prormt,
                    openai_template=openai_template,
                    model=model,
                )
                database_manager.save_compare_count(
                    file_name, openai_template, model, f'Reference{i}', response)
            else:
                print(f'{file_name}的第{i}段参考文献已经统计')


def clean_data(txt, count_dict):
    txt = txt.replace(' ', '')
    txt = txt.replace('\t', '')
    txt = txt.strip('|')
    txt = txt.split('|')[-1]
    txt = txt.strip('[]')
    replace = re.findall('（.*）', txt)
    if replace:
        txt = txt.replace(replace[0], '')
    count_list = list(count_dict.keys())[3:]
    for count in count_list:
        if count in txt:
            return count
    return txt


def eval_count(contents):
    rouge_l = 0
    bert_score = 0
    for content in contents:
        rouge_l += content[5]
        bert_score += content[6]
    rouge_l /= len(contents)
    bert_score /= len(contents)
    return rouge_l, bert_score
# 中文内容统计:中文摘要+正文


def aggregation(template, model, database_manager):
    table = pd.DataFrame()
    abstract_df = pd.DataFrame()
    file_list = get_file_list()
    for file_name in file_list:
        Abstract_list = database_manager.get_document(
            file_name, 'Abstract_Chinese')
        Abstract_len = sum([len(x[3]) for x in Abstract_list])
        Abstract_evals = database_manager.get_eval_count(
            file_name, template, model, 'Abstract_Chinese')
        if not Abstract_evals:
            print(f'正在统计{file_name}的中文摘要,摘要为空')
        rouge_l, bert_score = eval_count(Abstract_evals)
        Content_list = database_manager.get_document(file_name, 'Content')
        Content_len = sum([len(x[3]) for x in Content_list])
        count_dict = {'文件名': file_name,
                      '统计类型': '中文摘要',
                      '模型': model,
                      '句式错误': 0,
                      '语法错误': 0,
                      '用词不当': 0,
                      '错别字': 0,
                      '标点符号': 0,
                      '重复冗余': 0,
                      '逻辑问题': 0,
                      '术语规范': 0,
                      '总长度': Abstract_len,
                      'rougel': rouge_l,
                      'bert_score': bert_score,
                      }
        abstract_list = database_manager.get_compare_count(
            file_name, template, model, 'Abstract_Chinese')[0][5]
        print(f'正在统计{file_name}的中文摘要')
        abstract_list = abstract_list.split('\n')
        temp = count_dict.copy()
        for i, abstract in enumerate(abstract_list):
            abstract = clean_data(abstract, count_dict)
            if not abstract or abstract == '错误类型' or abstract.startswith('---') or '无错误' in abstract:
                continue
            if abstract in temp.keys():
                temp[abstract] += 1
            else:
                print(f'{file_name}的摘要统计结果有误')
                print(abstract_list[i])
        # 摘要统计
        table = pd.concat([table, pd.DataFrame.from_dict(
            temp, orient='index').T], ignore_index=True)
        sql = f"select * from compare_count where file_name='{file_name}' and model ='{model}' and content_tpye like 'Content%' order by id"
        Content_list = database_manager.custom(sql)
        print(f'正在统计{file_name}的内容')
        content_temp = []
        for i, content in enumerate(Content_list):
            content_temp.extend(content[5].split('\n'))
        count_dict['统计类型'] = '正文'
        count_dict['总长度'] = Content_len
        sql = f"select * from eval_count where file_name='{file_name}' and model ='{model}' and content_tpye like 'Content%' order by id"
        Content_eval = database_manager.custom(sql)
        rouge_l, bert_score = eval_count(Content_eval)
        count_dict['rougel'] = rouge_l
        count_dict['bert_score'] = bert_score
        temp = count_dict.copy()
        for i, content in enumerate(content_temp):
            if len(content) < 20:
                continue
            content = clean_data(content, count_dict)
            if content == '错误类型' or content.startswith('---'):
                continue
            if content in temp.keys():
                temp[content] += 1
            else:
                print(f'{file_name}的内容统计结果有误')
                print(content_temp[i])
        table = pd.concat([table, pd.DataFrame.from_dict(
            temp, orient='index').T], ignore_index=True)
        Abstract_list = database_manager.get_document(
            file_name, 'Abstract_English')
        Abstract_len = sum([len(x[3]) for x in Abstract_list])
        # 增加一个英文统计函数
        Abstract_evals = database_manager.get_eval_count(
            file_name, template, model, 'Abstract_English')
        rouge_l, bert_score = eval_count(Abstract_evals)
        count_dict = {'文件名': file_name,
                      '统计类型': '英文摘要',
                      '模型': model,
                      '句式错误': 0,
                      '语法错误': 0,
                      '拼写词汇错误': 0,
                      '术语使用错误': 0,
                      '格式规范错误': 0,
                      '数字单位错误': 0,
                      '空格使用错误': 0,
                      '总长度': Abstract_len,
                      'rougel': rouge_l,
                      'bert_score': bert_score,
                      }
        abstract_list = database_manager.get_compare_count(
            file_name, template, model, 'Abstract_English')[0][5]
        print(f'正在统计{file_name}的英文摘要')
        print(abstract_list)
        abstract_list = abstract_list.split('\n')
        temp = count_dict.copy()
        for i, abstract in enumerate(abstract_list):
            abstract = clean_data(abstract, count_dict)
            if not abstract or abstract == '错误类型' or abstract.startswith('---') or '无错误' in abstract:
                continue
            if abstract in temp.keys():
                temp[abstract] += 1
            else:
                print(f'{file_name}的英文摘要统计结果有误')
                print(abstract_list[i])
        abstract_df = pd.concat([abstract_df, pd.DataFrame.from_dict(
            temp, orient='index').T], ignore_index=True)
    table.to_excel(f'data/result/{model}_content.xlsx', index=False)
    abstract_df.to_excel(f'data/result/{model}_abstract.xlsx', index=False)


#  参考文献统计
def reference_count(template, model, database_manager):
    print(f'正在统计{model}的参考文献')
    table = pd.DataFrame()
    file_list = get_file_list()
    for file_name in file_list:
        Reference_list = database_manager.get_document(file_name, 'Reference')
        print(model, file_name)
        Reference_count = re.findall(
            r'\[(\d+)\].*?\n', Reference_list[-1][3])
        if Reference_count:
            Reference_count = Reference_count[-1]
        else:
            temp = Reference_list[-1][3].split('\n')
            temp = [x for x in temp if '参考文献' not in x]
            Reference_count = len(temp) 
        Reference_len = sum([len(x[3]) for x in Reference_list])
        sql = f"select * from eval_count where file_name='{file_name}' and model ='{model}' and content_tpye like 'Reference%' order by id"
        Reference_evals = database_manager.custom(sql)
        rouge_l, bert_score = eval_count(Reference_evals)
        count_dict = {'文件名': file_name,
                      '统计类型': '参考文献',
                      '模型': model,
                      '作者信息错误或不规范': 0,
                      '期刊或书籍名称格式问题': 0,
                      '文献类型混淆': 0,
                      '出版年与其他细节不一致': 0,
                      'DOI与其他信息遗漏或错误': 0,
                      '参考文献顺序错误': 0,
                      '中文和英文标点符号混用': 0,
                      '重复引用与排版问题': 0,
                      '页码与文章编号问题': 0,
                      '总长度': Reference_len,
                      '文献总数': Reference_count,
                      'rougel': rouge_l,
                      'bert_score': bert_score,
                      }
        sql = f"select * from compare_count where file_name='{file_name}' and model ='{model}' and content_tpye like 'Reference%' order by id"
        reference_list = database_manager.custom(sql)
        reference_temp = []
        for i, reference in enumerate(reference_list):
            reference_temp.extend(reference[5].split('\n'))
        print(f'正在统计{file_name}的参考文献')
        for i, reference in enumerate(reference_temp):
            reference = clean_data(reference, count_dict)
            if not reference or reference == '错误类型' or reference.startswith('---') or '无错误' in reference:
                continue
            if reference in count_dict.keys():
                count_dict[reference] += 1                
            else:
                score = 0
                match_key = ''
                for key in count_dict.keys():
                    temp_score = fuzz.ratio(key, reference)
                    if temp_score > score:
                        score = temp_score
                        match_key = key
                if score > 70:
                    count_dict[match_key] += 1
                else:
                    print(f'{file_name}的参考文献统计结果有误')
                    print(reference_temp[i])
        table = pd.concat([table, pd.DataFrame.from_dict(
            count_dict, orient='index').T], ignore_index=True)
    table.to_excel(f'data/result/{model}_reference.xlsx', index=False)
    print(f'大模型{model}的参考文献统计完成')


def SingleProcess(template, model):
    database_manager = DatabaseManager()
    file_list = get_file_list()
    # 第三步逐步处理每一个片段
    refine_llm(template, model, database_manager, file_list)
    # 第四步 统计
    compare_llm(template, model, database_manager, file_list)


def SingleCount(template, model):
    database_manager = DatabaseManager()
    file_list = get_file_list()
    eval_llm(template, model, database_manager, file_list)

def SingleAggregation(template, model):
    database_manager = DatabaseManager()
    aggregation(template, model, database_manager)
    reference_count(template, model, database_manager)
