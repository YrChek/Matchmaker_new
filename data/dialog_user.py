from data.bot_is_working import Working
from data.insert_db import DB
from data.search_users import Search
from data.tokkens import Tok_ken
# from main import token_app, token_group, db, boss_list
from data.logfiles.logs import log

token_group = input('Введите токен группы:' + '\n' + '--> ')
token_app = input('Введите токен приложения:' + '\n' + '--> ')
dbu = input('Введите адрес базы данных:' + '\n' + '--> ')
boss_list = input('Введите, через запятую, номера ID пользователей, имеющих право использования '
                  '"черного списка":' + '\n' + '--> ')

db = DB(token_group, token_app, dbu, boss_list)
letter = Working(token_group, token_app, dbu, boss_list)
found = Search(token_group, token_app, dbu, boss_list)
save = Tok_ken(token_group, token_app, dbu, boss_list)


def check_age(idu, message, array):
    """Проверка правильности введенного года рождения"""
    text = str()
    message = str(message)
    if len(message) != 4:
        text = f'Некорректная дата (длина)'
    else:
        for n in message:
            if n not in '0123456789':
                text = f'Некорректная дата (цифры)'
                break
    if 'Некорректная дата' in text:
        pass
    else:
        import time
        msg = int(message)
        year = time.localtime().tm_year
        if msg >= year - 18:
            text = f'Сервисом могут пользоваться только лица, {year - 19} года рождения и старше'
        else:
            array[idu].append(msg)
            text = f'Пришлите название вашего города (населенного пункта)'

    letter.write_msg(idu, text)
    return True


def name_city(idu, message, array):
    """Проверка названия города"""
    name = found.check_city(message)
    if name == 1:
        message = message.title()
        array[idu].append(message)
        text = 'Пришлите вашу половую принадлежность (муж/жен).'
        letter.write_msg(idu, text)
    elif name == 2:
        text = 'Населенный пункт не распознан, либо отсутствуют данные. ' \
               'Проверте правильность написания названия населенного пункта и пришлите заново.'
        letter.write_msg(idu, text)
    else:
        return False
    return True


def final_question(idu, message, array):
    """Проверка пола и отправка первой кандидатуры"""
    sex = 0
    if 'муж' in message:
        sex += 2
    if 'жен' in message:
        sex += 1
    if sex not in (1, 2):
        text = 'Ответ не распознан, проверте правильность написания. Пришлите слово "муж" или "жен"'
        letter.write_msg(idu, text)
    else:
        text = 'Ваш запрос принят, начинаем поиск. Потребуется некоторое время'
        letter.write_msg(idu, text)
        if 'муж' in message:
            sex = 2
        else:
            sex = 1
        array[idu].append(sex)
        mark = db.insert_users(idu, array)
        if not mark:
            full_name = array[idu][1]
            save.not_answered(idu, full_name, 'поиск')
            del array[idu]
            return False

        user_list = array[idu].copy()
        del array[idu]
        finish_list = found.candidat_list(user_list[0], user_list[2], user_list[3], user_list[4])
        if finish_list == 'error':
            full_name = user_list[1]
            save.not_answered(idu, full_name, 'отмена')
            return False
        elif len(finish_list) == 0:
            text = 'К сожалению по вашим параметрам кандидатов нет. Вы пожете прислать "Отмена"' \
                   ' и попробовать поиск с другими параметрами'
        else:
            mark = db.insert_user_candidate(finish_list)

            if not mark:
                full_name = user_list[1]
                save.not_answered(idu, full_name, 'отмена')
                return False

            list_id = db.select_city(user_list[0], user_list[3])
            if list_id == 'error':
                full_name = user_list[1]
                save.not_answered(idu, full_name, 'далее')
                return False

            ids = list_id[1]
            sort_list = found.photo_user(ids)
            if sort_list == 'error':
                full_name = user_list[1]
                save.not_answered(idu, full_name, 'далее')
                return False

            save.writing_last(list_id)
            letter.photos_message(idu, ids, sort_list)
            mark = db.delete_record(idu, ids)
            if not mark:
                text = 'Приносим извинения, технический сбой. Могут быть повторные предложения'
            else:
                text = 'Пришлите "далее", чтобы посмотреть следующую кандидатуру/\n' \
                       'Пришлите "сохранить", что бы добавить кандидатуру в избранное.'
        letter.write_msg(idu, text)
    return True


def continue_selection(idu, message, array):
    """Отправка следуещего кандидата"""

    if 'далее' not in message:
        text = 'Запрос не распознан. Проверте правильность написания.\n' \
               'Для нового поиска наберите "Далее" .\n' \
               'Для добавления в избранное, наберите "Сохраниить".\n' \
               'Что бы посмотеть всех избранных, наберите "Показать".\n' \
               'Что бы удалить из избранного, наберите "Удалить"\n' \
               'Для изменения параметров поиска, наберите "Отмена".'
        letter.write_msg(idu, text)
    else:
        user_list = array[idu]
        del array[idu]
        list_id = db.select_city(user_list[0], user_list[3])
        if list_id == 'error':
            full_name = user_list[1]
            save.not_answered(idu, full_name, 'далее')
            return False
        if list_id is None:
            text = 'К сожалению, в вашем городе, закончились все кандидаты.\n ' \
                   'Наберите "Отмена" и попробуйте выбрать другой населенный пункт.'
        else:
            ids = list_id[1]
            sort_list = found.photo_user(ids)
            if sort_list == 'error':
                full_name = user_list[1]
                save.not_answered(idu, full_name, 'далее')
                return False

            save.writing_last(list_id)
            letter.photos_message(idu, ids, sort_list)
            mark = db.delete_record(idu, ids)
            if not mark:
                text = 'Приносим извинения, технический сбой. Могут быть повторные предложения'
            else:
                text = 'Пришлите "далее", чтобы посмотреть следующую кандидатуру/\n' \
                       'Пришлите "сохранить", что бы добавить кандидатуру в избранное.'
        letter.write_msg(idu, text)
    return True


def dialog_users(idu, message, cells, array):
    """функция - маршрутизатор при диалоге в поиске кандидатов"""
    if cells == 2:
        check_age(idu, message, array)
    elif cells == 3:
        mark = name_city(idu, message, array)
        if not mark:
            return False
    elif cells == 4:
        mark = final_question(idu, message, array)
        if not mark:
            return False
    elif cells == 5:
        mark = continue_selection(idu, message, array)
        if not mark:
            return False
    else:
        log.error('Ошибка dialog_user')
    return True


def favourites_del(idu, message):
    """Удаление из избранного"""
    idu = int(idu)
    num = ''
    for i in message:
        if i in '0123456789':
            num += i

    if 'всех' in message:
        every = db.select_all_favourites(idu)
        if every != 'error':
            if len(every) != 0:
                deleting = db.delete_all_favourites(idu)
                if deleting:
                    text = 'Избранное очищено'
                    output = 'good'
                else:
                    log_text = f'Ошибка удаления избранных\n{idu} -> delete_all_favourites'
                    log.warning(log_text)
                    text = 'Неудачная попытка удаления'
                    output = 'error'
            else:
                text = 'У Вас нет избранного'
                output = 'good'
        else:
            log_text = f'Ошибка подключения к БД\n{idu} -> delete_all_favourites'
            log.warning(log_text)
            text = 'Техническая неисправность, приносим свои извенения! Скоро все заработает.'
            output = 'error'
        letter.write_msg(idu, text)
        return output

    elif len(num) != 0:
        if len(num) != 9:
            text = 'Неверный номер id пользователя'
            output = 'good'
        else:
            ids = int(num)
            some = db.select_favourite(idu, ids)
            if some != 'error':
                if len(some) != 0:
                    deleting = db.delete_favourite(idu, ids)
                    if deleting:
                        text = f'Пользователь {some[2]} удален из избранного'
                        output = 'good'
                    else:
                        log_text = f'Ошибка удаления избранного\n{idu} -> {ids}'
                        log.warning(log_text)
                        text = 'Неудачная попытка удаления'
                        output = 'error'
                else:
                    text = 'Этот пользователь отсутствует в сохраненных'
                    output = 'good'
            else:
                log_text = f'Ошибка подключения к БД\n{idu} -> select_favourite {ids}'
                log.warning(log_text)
                text = 'Техническая неисправность, приносим свои извенения! Скоро все заработает.'
                output = 'error'
        letter.write_msg(idu, text)
        return output

    else:
        text = 'Для полного удаления избранного наберите "Удалить всех".\n ' \
               'Для удаления одного пользователя, наберите "Удалить *********", ' \
               'где вместо звездочек наберите номер id удаляемого пользователя.\n' \
               'Что бы посмотеть всех избранных, наберите "Показать"'
        output = 'good'
        letter.write_msg(idu, text)
    return output


def favourites_in(idu):
    """Добавление пользователя в избранное"""
    ids_list = save.read_last(idu)
    if ids_list:
        data = [int(idu), int(ids_list[0]), ids_list[1]]
        paste = db.insert_favourite(data)
        if paste:
            text = f'Пользователь {ids_list[1]} добавлен в избранное.\n' \
                   f'Вы можете удалить пользователя из сохраненных набрав команду "Удалить"\n' \
                   f'Что бы посмотеть всех избранных, наберите "Показать"'
            output = 'good'
        else:
            log_text = f'Ошибка сохранения избранного\n{idu} -> [{ids_list[0]} {ids_list[1]}]'
            log.warning(log_text)
            text = 'Неудачная попытка сохранения пользователя'
            output = 'error'
    else:
        text = 'Ваша команда не распознана, проверьте правильность написания.\n ' \
               'Если вы желаете найти себе спутника, либо начать интересное общение, ' \
               'наберите "Поиск".'
        output = 'good'
    letter.write_msg(idu, text)
    return output


def favourites_com(idu):
    """Показать всех избранных клиента"""
    every = db.select_all_favourites(idu)
    if every != 'error':
        if len(every) != 0:
            text = 'Ваши избранные:\n'
            output = 'good'
            for some in every:
                text += f'{some[2]} https://vk.com/{some[1]}\n'
        else:
            text = 'У Вас нет избранного'
            output = 'good'
    else:
        log_text = f'Ошибка подключения к БД\n{idu} -> select_all_favourites'
        log.warning(log_text)
        text = 'Техническая неисправность, приносим свои извенения! Скоро все заработает.'
        output = 'error'
    letter.write_msg(idu, text)
    return output


def dialog_favourites(idu, message):
    """функция - маршрутизатор при диалоге в работе с избранным"""
    if 'сохран' in message:
        mark = favourites_in(idu)
        if mark == 'error':
            return False

    elif 'удалит' in message:
        mark = favourites_del(idu, message)
        if mark == 'error':
            return False

    elif 'показат' in message:
        mark = favourites_com(idu)
        if mark == 'error':
            return False

    else:
        log.error('Ошибка dialog_favourites')
        return False

    return True
