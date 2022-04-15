import os


class Tok_ken:

    def __init__(self, token_group, token_app, db, boss_list):
        self.token_group = token_group
        self.token_app = token_app
        self.db = db
        self.boss_list = boss_list
        self.status = True

    def not_answered(self, idu, full_name, message):
        """запись входящего сообщения в файл при работе без БД"""
        path = os.getcwd()
        full_path = os.path.join(path, 'data', 'logfiles', 'in_waiting.txt')
        text = f'{idu}, {full_name}, {message}\n'
        with open(full_path, 'a', encoding='utf-8') as file:
            file.write(text)
        return True

    def reading_unanswered(self):
        """чтение файла in_waiting.txt"""
        path = os.getcwd()
        full_path = os.path.join(path, 'data', 'logfiles', 'in_waiting.txt')
        waiting_list = []
        with open(full_path, encoding='utf-8') as file:
            for line in file.readlines():
                line = line.strip()
                waiting_list.append(line.split(','))
        return waiting_list

    def clearing_file(self):
        """очистка файла in_waiting.txt"""
        path = os.getcwd()
        full_path = os.path.join(path, 'data', 'logfiles', 'in_waiting.txt')
        with open(full_path, 'w') as file:
            file.write('')
        return True

    def writing_last(self, array):
        """создание или перезапись файла последнего отправленного кандидата"""
        name_file = f'{array[0]}'
        text = f'{array[1]}, {array[2]}'
        path = os.getcwd()
        full_path = os.path.join(path, 'data', 'last_sent', name_file)
        with open(full_path, 'w', encoding='utf-8') as file:
            file.write(text)
        return True

    def read_last(self, idu):
        """чтение из файла последнего отправленного"""
        idu = str(idu)
        path = os.getcwd()
        full_path = os.path.join(path, 'data', 'last_sent', idu)
        if not os.path.exists(full_path):
            return False
        else:
            with open(full_path, encoding='utf-8') as file:
                line = file.readline()
            line = line.strip()
            ids_list = line.split(',')
            return ids_list

    def delete_last(self, idu):
        """удаление файла"""
        idu = str(idu)
        path = os.getcwd()
        full_path = os.path.join(path, 'data', 'last_sent', idu)
        if os.path.isfile(full_path):
            os.remove(full_path)
