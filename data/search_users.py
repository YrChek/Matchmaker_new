from data.tokkens import Tok_ken
from data.logfiles.logs import log
import vk_api
import time


class Search(Tok_ken):

    def app_vk(self):
        vk = vk_api.VkApi(token=self.token_app)
        return vk

    def search_users(self, city, sex, user_date):
        """Поиск всех пользователей в VK по городу и полу со статусом в активном поиске"""
        vk = self.app_vk()
        user_dict = {}
        if sex == 1:
            lower_age_limit = user_date + 7
            upper_age_limit = user_date - 3
        elif sex == 2:
            lower_age_limit = user_date + 2
            upper_age_limit = user_date - 8
        current_year = time.localtime().tm_year
        age_censor = current_year - 18
        if lower_age_limit >= age_censor:
            lower_age_limit = age_censor
        birth_year = lower_age_limit
        resp = 0
        while birth_year >= upper_age_limit:
            params = {'fields': 'city,bdate,sex,relation', 'birth_year': birth_year,
                      'hometown': city, 'sex': sex, 'status': 6, 'count': 1000, 'v': 5.131}
            try:
                res = vk.method('users.search', params)
            except Exception as error:
                log.error("Ошибка запроса поиска кандидатов", exc_info=True)
                print('Ошибка запроса к VK:\n', error)
                return 'error'
            birth_year -= 1
            time.sleep(0.34)
            resp += 1
            n = len(res['items'])
            for i in res['items']:
                idu = i['id']
                if idu not in user_dict:
                    user_dict[idu] = i
        return user_dict

    def select_users(self, array, idu, user_date, user_sex):
        """Отбор пользователей с открытой страницей и полными основными данными"""
        names = []
        for key, data in array.items():
            temp_names = []

            if data['is_closed']:
                continue
            temp_names.append(int(idu))

            if 'id' in data:
                ids = data['id']
            else:
                continue
            temp_names.append(int(ids))

            if 'first_name' in data:
                name = data['first_name']
                if 'last_name' in data:
                    last = data['last_name']
                    full_name = f'{name} {last}'
                else:
                    full_name = name
                temp_names.append(full_name)
            else:
                continue

            if 'bdate' in data:
                bdate = data['bdate']
                if len(bdate) > 5:
                    number = True
                    for i in bdate[-4:]:
                        if i not in '0123456789':
                            number = False
                            break
                    if number:
                        year = int(bdate[-4:])
                    else:
                        continue
                else:
                    continue
                current_year = time.localtime().tm_year
                user_date = int(user_date)
                if year > current_year - 18:
                    continue
                if user_sex == 1:
                    lower_age_limit = user_date + 2
                else:
                    lower_age_limit = user_date + 7
                if year > lower_age_limit:
                    continue
                temp_names.append(year)
            else:
                continue

            if 'city' in data:
                if 'title' in data['city']:
                    city = data['city']['title']
                    temp_names.append(city)
                else:
                    continue
            else:
                continue

            if 'sex' not in data:
                continue
            temp_names.append(int(data['sex']))

            if 'relation' in data:
                if data['relation'] == 6:
                    pass
                else:
                    continue
            else:
                continue

            names.append(temp_names)

        return names

    def candidat_list(self, idu, user_date, city, user_sex):
        """Список отобранных кандидатов"""
        sex = 3 - user_sex
        array = self.search_users(city, sex, user_date)
        if array == 'error':
            return 'error'
        finish_list = self.select_users(array, idu, user_date, user_sex)
        return finish_list

    def photo_user(self, ids):
        """Выбор фотографий конкретного пользователя"""
        not_sorted_list = []
        vk = self.app_vk()
        params = {'owner_id': ids, 'album_id': 'profile', 'rev': '1', 'extended': '1', 'count': '20'}
        try:
            photos = vk.method('photos.get', params)
        except Exception as error:
            log.error("Ошибка при запросе названия города", exc_info=True)
            return 'error'
        for data in photos['items']:
            rating = data['likes']['count'] + data['comments']['count']
            not_sorted_list += [[rating, data['sizes'][-1]['url']]]
        sort_list = sorted(not_sorted_list)
        if len(sort_list) > 3:
            return sort_list[-3:]
        else:
            return sort_list

    def check_city(self, city):
        """Проверка наличия города"""
        vk = self.app_vk()
        params = {'country_id': '1', 'q': city, 'count': '1'}
        try:
            response = vk.method('database.getCities', params)
        except Exception as error:
            log.error("Ошибка при запросе названия города", exc_info=True)
            return 3
        if response['count'] != 0:
            return 1
        else:
            return 2