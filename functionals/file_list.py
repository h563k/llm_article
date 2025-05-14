import os
import json
from functionals.save_data import DatabaseManager
def get_file_list():
    temp_list = []
    database_manager = DatabaseManager()
    db_path = database_manager.db_path
    db_path = os.path.dirname(db_path)
    db_path = os.path.join(db_path, 'file_list.json')
    file_list = database_manager.get_documents_file_names()
    with open(db_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    for list in file_list:
        if list not in data:
            temp_list.append(list)
    return file_list
    
