from data.bot_is_working import Working
from data.insert_db import DB

from data.dialog_user import token_group, token_app, dbu, boss_list


if __name__ == '__main__':
    create_db = DB(token_group, token_app, dbu, boss_list)
    create_db.create_table()
    start = Working(token_group, token_app, dbu, boss_list)
    start.working_bot()
