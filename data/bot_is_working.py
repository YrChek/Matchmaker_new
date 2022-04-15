import os
from io import BytesIO
from random import randrange

import requests
import vk_api
from vk_api import VkUpload
from vk_api.longpoll import VkLongPoll, VkEventType

from data.insert_db import DB
from data.logfiles.logs import log
from data.tokkens import Tok_ken


class Working(Tok_ken):

    def __init__(self, token_group, token_app, db, boss_list):
        super().__init__(token_group, token_app, db, boss_list)
        self.data = DB(token_group, token_app, db, boss_list)
        self.attachment = False
        self.owner_ida = False
        self.photo_ids = False

    def group_vk(self):
        vk = vk_api.VkApi(token=self.token_group)
        return vk

    def write_msg(self, user_id, message):
        """Отправка текстового сообщения"""
        vk = self.group_vk()
        vk.method('messages.send', {'user_id': user_id, 'message': message, 'random_id': randrange(10 ** 7), })
        log.info(f'ответ пользователю id{user_id}:\n "{message}"')

    def photos_message(self, idu, ids, array):
        """Зазгузка и отправка фотографий клиенту"""

        vk = self.group_vk()
        vk_upload = vk.get_api()
        upload = VkUpload(vk_upload)
        text = f'Ссылка на страницу в ВК: https://vk.com/id{ids}'
        self.write_msg(idu, text)
        for image_url in array:
            image_url = image_url[1]
            img = requests.get(image_url).content
            photo_bytes = BytesIO(img)
            try:
                image = upload.photo_messages(photo_bytes)[0]
            except Exception:
                log.error("Ошибка при скачивании фотографии", exc_info=True)
                text = 'Техническая неисправность, приносим свои извинения! Скоро все заработает.'
                self.write_msg(idu, text)
                return False
            owner_id = image['owner_id']
            photo_id = image['id']
            peer_id = idu
            photo_bytes.close()
            print(f'фотография id{photo_id} скачана')

            text = f'Фотография из профиля'
            attachment = f'photo{str(owner_id)}_{str(photo_id)}'
            params = {'peer_id': peer_id, 'message': text, 'attachment': attachment, 'random_id': randrange(10 ** 7)}
            try:
                vk.method('messages.send', params)
            except Exception:
                log.error("Ошибка при отправке фотографии пользователю", exc_info=True)
                text = 'Техническая неисправность, приносим свои извинения! Скоро все заработает.'
                self.write_msg(idu, text)
                return False
        log.info(f'фотографии пользователю id{idu} отправлены"')
        return True

    def client_name(self, idu):
        """Поиск данных о клиенте"""
        vk = self.group_vk()
        params_user = {'user_ids': idu, 'fields': 'city'}
        try:
            res = vk.method('users.get', params_user)[0]
        except Exception:
            log.error("Ошибка поиска данных о клиенте", exc_info=True)
            text = 'Техническая неисправность, приносим свои извинения! Скоро все заработает.'
            self.write_msg(idu, text)
            return False
        name = res['first_name']
        data_list = []
        idu = int(idu)
        data_list.append(idu)

        if 'last_name' in res and len(res['last_name']) != 0:
            full_name = f'{res["first_name"]} {res["last_name"]}'
        else:
            full_name = {res['first_name']}
        data_list.append(full_name)

        if 'city' in res:
            if 'title' in res['city'] and len(res['city']['title']) != 0:
                city = res['city']['title']
                data_list.append(city)
        else:
            city = ''
            data_list.append(city)

        data_list.append(name)

        return data_list

    def many_messages(self, idu, message, full_name, user_dict, list_blocked):
        vk = self.group_vk()
        mark = ''
        if 'отмен' in message:
            idu = int(idu)
            clearing_search = self.data.clearing_search(idu)
            if not clearing_search:
                self.status = False
                self.not_answered(idu, full_name, message)
                print('Функциональность бота ограничена.')
                text = 'Техническая неисправность, приносим свои извенения! Скоро все заработает.'
                self.write_msg(idu, text)
                return False
            delete_data_user = self.data.delete_data_user(idu)
            if not delete_data_user:
                self.status = False
                self.not_answered(idu, full_name, message)
                print('Функциональность бота ограничена.')
                text = 'Техническая неисправность, приносим свои извенения! Скоро все заработает.'
                self.write_msg(idu, text)
                return False
            clearing_search = self.data.clearing_search(idu)
            if not clearing_search:
                self.status = False
                self.not_answered(idu, full_name, message)
                print('Функциональность бота ограничена.')
                text = 'Техническая неисправность, приносим свои извенения! Скоро все заработает.'
                self.write_msg(idu, text)
                return False
            if idu in user_dict:
                del user_dict[idu]
            self.delete_last(idu)
            text = 'Параметры удалены. Вы можете набрать "Поиск" и ввести новые данные'
            self.write_msg(idu, text)

        elif "поиск" in message:
            from data.dialog_user import dialog_users
            idu = int(idu)
            user = self.data.select_user(idu)

            if user == 'error':
                mark = 'error'
                self.status = False
                self.not_answered(idu, full_name, message)
                print('Функциональность бота ограничена.')
            else:
                if user is not None:
                    if user[0] not in user_dict:
                        user_dict[idu] = user

            if idu in user_dict:
                mark = 'good'

            if mark == 'good':
                cells = len(user_dict[idu])
                quest = dialog_users(idu, message, cells, user_dict)
                if not quest:
                    self.status = False
                    self.not_answered(idu, full_name, message)
                    print('Функциональность бота ограничена.')
                    text = 'Техническая неисправность, приносим свои извенения! Скоро все заработает.'
                    self.write_msg(idu, text)

            elif mark == 'error':
                text = 'Техническая неисправность, приносим свои извенения! Скоро все заработает.'
                self.write_msg(idu, text)

            else:
                user_dict[idu] = [idu, full_name]
                text = 'Пришлите год вашего рождения'
                self.write_msg(idu, text)

        elif 'unlock' in message:
            boss = str(idu)
            if boss in self.boss_list:
                peer_id = ''
                for i in message:
                    if i in '0123456789':
                        peer_id += i
                if len(peer_id) != 9:
                    text = 'некорректный номер id пользователя'
                elif int(peer_id) not in list_blocked:
                    text = 'пользователь отсутствует в черном списке'
                else:
                    ids = int(peer_id)
                    restore = self.data.clearing_banned(ids)
                    if restore:
                        list_blocked.remove(ids)
                        self.write_msg(ids, 'Вы снова можете пользоваться сервисом!')
                        log.info(f'сообщение пользователю id{ids}:\n '
                                 f'"Вы снова можете пользоваться сервисом!"')
                        text = 'пользователь удален из черного списка'
                    else:
                        text = 'неудачная попытка удаления из черного списка'
                self.write_msg(idu, text)
            else:
                text = 'У вас нет прав, для выполнения этого действия'
                self.write_msg(idu, text)

        elif 'lock' in message:
            boss = str(idu)
            if boss in self.boss_list:
                peer_id = ''
                for i in message:
                    if i in '0123456789':
                        peer_id += i
                if len(peer_id) != 9:
                    text = 'некорректный номер id пользователя'
                else:
                    if self.attachment:
                        attachment = self.attachment
                        peer_id = int(peer_id)
                        data_list = [peer_id, self.owner_ida, self.photo_ids]
                        work = self.data.insert_banned(data_list)
                        if work:
                            list_blocked.append(peer_id)
                            params = {'peer_id': peer_id, 'attachment': attachment,
                                      'random_id': randrange(10 ** 7)}
                            vk.method('messages.send', params)
                            log.info(f'Картинка пользователю id{peer_id}:\n '
                                     f'"Вы добавлены в черный список"')
                            text = 'Пользователь в черный список добавлен'
                        else:
                            text = 'неудачная попытка добавления в черный список'
                    else:
                        peer_id = int(peer_id)
                        vk_upload = vk.get_api()
                        upload = VkUpload(vk_upload)
                        path = os.getcwd()
                        name_file = os.path.join(path, 'data', 'pictures', 'ban.png')
                        try:
                            photo = upload.photo_messages(name_file)[0]
                        except Exception:
                            photo = 'error'
                            log.error("Ошибка скачивании фото с диска", exc_info=True)
                        if photo != 'error':
                            owner_id = photo['owner_id']
                            photo_id = photo['id']
                            data_list = [peer_id, int(owner_id), int(photo_id)]
                            work = self.data.insert_banned(data_list)
                            if work:
                                self.owner_ida = owner_id
                                self.photo_ids = photo_id
                                list_blocked.append(peer_id)
                                attachment = f'photo{owner_id}_{photo_id}'
                                self.attachment = attachment
                                params = {'peer_id': peer_id, 'attachment': attachment,
                                          'random_id': randrange(10 ** 7)}
                                vk.method('messages.send', params)
                                log.info(f'Картинка пользователю id{peer_id}:\n '
                                         f'"Вы добавлены в черный список"')
                                text = 'Пользователь добавлен в черный список'
                            else:
                                text = 'попытка добавления в черный список не удалась'
                        else:
                            text = 'в черный список не добавлено'

                self.write_msg(idu, text)
            else:
                text = 'У вас нет прав, для выполнения этого действия'
                self.write_msg(idu, text)

        elif 'сохран' in message:
            from data.dialog_user import dialog_favourites
            idu = int(idu)
            mark = dialog_favourites(idu, message)
            if not mark:
                self.not_answered(idu, full_name, message)

        elif 'удалить' in message:
            from data.dialog_user import dialog_favourites
            idu = int(idu)
            mark = dialog_favourites(idu, message)
            if not mark:
                self.not_answered(idu, full_name, message)

        elif 'показать' in message:
            from data.dialog_user import dialog_favourites
            idu = int(idu)
            mark = dialog_favourites(idu, message)
            if not mark:
                self.not_answered(idu, full_name, message)

        else:
            from data.dialog_user import dialog_users
            idu = int(idu)
            user = self.data.select_user(idu)
            if user == 'error':
                mark = 'error'
                self.status = False
                self.not_answered(idu, full_name, message)
                print('Функциональность бота ограничена.')
            else:
                if user is not None:
                    if user[0] not in user_dict:
                        user_dict[idu] = user

            if idu in user_dict:
                mark = 'good'

            if mark == 'good':
                cells = len(user_dict[idu])
                quest = dialog_users(idu, message, cells, user_dict)
                if not quest:
                    self.status = False
                    self.not_answered(idu, full_name, message)
                    print('Функциональность бота ограничена.')
                    text = 'Техническая неисправность, приносим свои извенения! Скоро все заработает.'
                    self.write_msg(idu, text)

            elif mark == 'error':
                text = 'Техническая неисправность, приносим свои извенения! Скоро все заработает.'
                self.write_msg(idu, text)

            else:
                text = 'Ваша команда не распознана, проверьте правильность написания.\n ' \
                       'Если вы желаете найти себе спутника, либо начать интересное общение, ' \
                       'наберите "Поиск".'
                self.write_msg(idu, text)

    def working_bot(self):
        print('start working_bot')
        vk = self.group_vk()
        user_dict = {}
        list_blocked = []

        access_db = self.data.select_all_users()  # проверка доступности БД
        if access_db == 'error':
            print('Остановка работы бота')
            return

        blocked = self.data.select_banned()
        if blocked == 'error':
            log.warning('Ошибка чтения черного списка')
            print('работа бота без учета черного списка')
        else:
            if len(blocked) != 0:
                self.owner_ida = blocked[0][1]
                self.photo_ids = blocked[0][2]
                self.attachment = f'photo{self.owner_ida}_{self.photo_ids}'
                for block in blocked:
                    list_blocked.append(block[0])

        waiting_list = self.reading_unanswered()
        self.clearing_file()
        if len(waiting_list) != 0:
            waiting_idu_list = []
            for line in waiting_list:
                print(line)
                idu = int(line[0])
                if idu not in waiting_idu_list:
                    waiting_idu_list.append(idu)
                    text = 'Технические проблеммы устранены. Мы снова с вами!'
                    self.write_msg(idu, text)
                    self.many_messages(idu, line[2], line[1], user_dict, list_blocked)
            del waiting_idu_list

        longpoll = VkLongPoll(vk)
        for event in longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW:
                idu = event.user_id

                if event.to_me:
                    if idu in list_blocked:
                        pass
                    else:
                        message = event.text.lower()
                        data_user = self.client_name(idu)
                        full_name = data_user[1]
                        log.info(f'запрос от пользователя id{idu}:\n "{message}"')

                        if message in 'привет!привет.зравствуйте.здравствуйте!здрасте.здрасте!':
                            text = f'Здравствуйте, {data_user[-1]}!\n' \
                                   f'Если вы желаете найти себе спутника, либо начать интересное общение, ' \
                                   f'наберите "Поиск".\n' \
                                   f'Если вы хотите продолжить поиск, наберите "Далее".'
                            self.write_msg(idu, text)

                        elif message in 'пока.пока!досвидания.досвидания!':
                            text = f'Всего хорошего, {data_user[-1]}!'
                            self.write_msg(idu, text)

                        elif message in 'спасибо.спасибо!':
                            text = 'Рады были помочь!'
                            self.write_msg(idu, text)

                        elif not self.status:
                            self.not_answered(idu, full_name, message)
                            text = 'Извините, временные неполадки!'
                            self.write_msg(idu, text)

                        else:
                            self.many_messages(idu, message, full_name, user_dict, list_blocked)
