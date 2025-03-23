import os
import sqlite3
from datetime import datetime
import pytz


class DatabaseManager:
    def __init__(self, db_path="paper_checker.db"):
        self.db_path = self.get_path(db_path)
        self.init_db()

    def init_db(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        """
        创建 documents 表 此表用于储存论文分割后的结果
        """
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS documents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                file_name TEXT NOT NULL,
                content_type TEXT NOT NULL,
                content TEXT,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        """
        创建 summarize 表 此表用于总结全文
        """
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS summarize (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                file_name TEXT NOT NULL,
                content TEXT,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # 创建 reference_cache 表用于统计全文对比的结果
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS reference_cache (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                file_name TEXT NOT NULL,
                template TEXT NOT NULL,
                model TEXT NOT NULL,
                content_tpye TEXT,
                content TEXT,
                reference TEXT,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # 创建 compare_count 表用于统计错误
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS compare_count (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                file_name TEXT NOT NULL,
                template TEXT NOT NULL,
                model TEXT NOT NULL,
                content_tpye TEXT,
                reference TEXT,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # 创建 eval_count 表用于计算评估
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS eval_count (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                file_name TEXT NOT NULL,
                template TEXT NOT NULL,
                model TEXT NOT NULL,
                content_tpye TEXT,
                rouge_l FLOAT,
                bert_score FLOAT,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()
        conn.close()

    @staticmethod
    def current():
        # 设置为中国标准时间（CST）
        cst = pytz.timezone('Asia/Shanghai')
        now = datetime.now(cst)
        formatted_time = now.strftime('%Y-%m-%d %H:%M:%S')
        return formatted_time

    def get_path(self, db_path):
        path = os.path.abspath(__file__)
        path = os.path.dirname(path)
        path = os.path.dirname(path)
        path = os.path.join(path, 'data')
        path = os.path.join(path, 'db')
        db_path = os.path.join(path, db_path)
        return db_path

    def _get_connection(self):
        return sqlite3.connect(self.db_path)

    def save_eval_count(self, file_name, template, model, content_tpye, rouge_l, bert_score):
        formatted_time = self.current()
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO eval_count (file_name, template, model, content_tpye, rouge_l, bert_score, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (file_name, template, model, content_tpye, rouge_l, bert_score, formatted_time))

        conn.commit()
        conn.close()

    def get_eval_count(self, file_name, template, model, content_tpye):
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            select * from eval_count where 
            file_name = ? and template = ? and model = ?  and content_tpye = ? order by id
        ''', (file_name, template, model, content_tpye))
        result = cursor.fetchall()
        conn.close()
        return result

    def save_document(self, file_name, content_type, content):
        formatted_time = self.current()
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO documents (file_name, content_type, content, updated_at)
            VALUES (?, ?, ?, ?)
        ''', (file_name, content_type, content, formatted_time))

        conn.commit()
        conn.close()

    def get_document(self, file_name, content_type=None):
        conn = self._get_connection()
        cursor = conn.cursor()
        if not content_type:
            cursor.execute(
                "select * from documents where file_name = ? order by id", (file_name, ))
        else:
            cursor.execute(
                "select * from documents where file_name = ? and content_type = ? order by id", (file_name, content_type))
        result = cursor.fetchall()
        conn.close()
        return result

    def get_documents_file_names(self):
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute('select distinct file_name from documents order by id')
        result = cursor.fetchall()
        conn.close()
        return [row[0] for row in result]

    def save_summarize(self, file_name, content):
        formatted_time = self.current()
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO summarize (file_name, content, updated_at)
            VALUES (?, ?, ?)
        ''', (file_name, content, formatted_time))
        conn.commit()
        conn.close()

    def get_summarize(self, file_name):
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "select * from summarize where file_name = ? order by id", (file_name, ))
        result = cursor.fetchall()
        conn.close()
        return result[0] if result else None

    def save_reference_cache(self, file_name, template, model, content_tpye, content, reference):
        formatted_time = self.current()
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO reference_cache (file_name, template, model, content_tpye, content, reference, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (file_name, template, model, content_tpye, content, reference, formatted_time))
        conn.commit()
        conn.close()

    def get_reference_cache(self, file_name, template, model, content_tpye):
        sql = "select * from reference_cache where file_name = ? and template = ? and model = ? and content_tpye=? order by id"
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute(sql, (file_name, template, model, content_tpye))
        result = cursor.fetchall()
        conn.close()
        return result

    def save_compare_count(self, file_name, template, model, content_tpye, reference):
        formatted_time = self.current()
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO compare_count (file_name, template, model, content_tpye, reference, updated_at)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (file_name, template, model, content_tpye, reference, formatted_time))
        conn.commit()
        conn.close()

    def get_compare_count(self, file_name, template, model, content_tpye):
        sql = "select * from compare_count where file_name = ? and template = ? and model = ? and content_tpye=? order by id"
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute(sql, (file_name, template, model, content_tpye))
        result = cursor.fetchall()
        conn.close()
        return result

    def custom(self, txt):
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute(txt)
        result = cursor.fetchall()
        conn.close()
        return result
