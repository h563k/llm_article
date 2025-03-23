from rouge import Rouge
from bert_score import score
from transformers import BertTokenizer


def custom_tokenizer(text):
    # 加载预训练的tokenizer
    tokenizer = BertTokenizer.from_pretrained('bert-base-chinese')

    # 使用tokenizer进行分词
    tokens = tokenizer.tokenize(text)

    # 输出分词结果
    return tokens


def rouge_l(reference_summary: str, predicted_summary: str) -> dict:
    # 初始化ROUGE对象
    rouge = Rouge()
    reference_summary = custom_tokenizer(reference_summary)
    predicted_summary = custom_tokenizer(predicted_summary)
    # 将分词结果转换为字符串形式，每个词之间用空格隔开
    reference_summary = ' '.join(reference_summary)
    predicted_summary = ' '.join(predicted_summary)
    # 计算ROUGE分数
    scores = rouge.get_scores(predicted_summary, reference_summary, avg=True)

    # 输出ROUGE-L分数
    return scores['rouge-l']


def bert_score_eval(reference_summary: str, predicted_summary: str) -> dict:
    # 初始化BERTScorer，指定本地模型路径
    # 计算BERTScore
    P, R, F1 = score([predicted_summary], [reference_summary], lang='zh')

    # 返回BERTScore的精确度(P)、召回率(R)和F1分数
    return {
        'precision': P.mean().item(),
        'recall': R.mean().item(),
        'f1': F1.mean().item()
    }


def eval(reference_summary: str, predicted_summary: str) -> dict:
    # 计算ROUGE分数
    rouge_scores = rouge_l(reference_summary, predicted_summary)
    # 计算BERTScore
    bert_scores = bert_score_eval(reference_summary, predicted_summary)
    eval_scores = {
        'rouge_l': rouge_scores['f'],
        'bert_score': bert_scores['f1']
    }
    return eval_scores


if __name__ == '__main__':
    """
    {'r': 0.7777777777777778, 'p': 0.5833333333333334, 'f': 0.6666666617687076}
    {'precision': 0.844964861869812, 'recall': 0.9098458290100098, 'f1': 0.8762059211730957}
    """
    reference_summary = "This is a reference summary."
    predicted_summary = "This is a predicted summary too."
    eval_scores = eval(reference_summary, predicted_summary)
    print(eval_scores)
