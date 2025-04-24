# %%
# 此脚本必须使用windows系统, 并安装word软件

# %%
import os
from win32com import client

# %%
def convert_doc_to_docx(doc_path, docx_path):
    # 启动Word应用程序
    word = client.Dispatch("Word.Application")
    word.Visible = False

    try:
        # 打开.doc文件
        doc = word.Documents.Open(doc_path)
        # 保存为.docx文件
        doc.SaveAs(docx_path, FileFormat=16)  # 16 是 .docx 的文件格式代码
        doc.Close()
        os.remove(doc_path)
    except Exception as e:
        print(f"转换失败: {e}")
    finally:
        # 关闭Word应用程序
        word.Quit()



# %%
file_path = os.getcwd()
original_data = os.path.join(file_path, "data", 'original_artcle')

# %%
_, _, paths = os.walk(original_data).__next__()
for path in paths:
    if path.endswith('.doc'):
        doc_path = os.path.join(original_data, path)
        docx_path = f'{doc_path}x'
        print(f"开始转换{path}文件")
        convert_doc_to_docx(doc_path, docx_path)


