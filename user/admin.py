import os
import sys


try:
    from common.utils import get_id, name_util
    from database_interface import Database
except Exception as e:
    sys.path.append('/home/a/projects/flask-photo-site')
    print(sys.path)

    for fuckyoupython in sys.path:
        print('\n', fuckyoupython)
    from common.password_util import PasswordUtil
    from database_interface import Database


class Admin(object):
    def __init__(self):
        self.db = Database('eigi-data.db')

    def make_account(self, username, password):
        self.db.make_query(
            '''
            insert into user (user_id, username, hash_value)
            values ("{}", "{}", "{}")
            '''.format(
                username,
                password,
                PasswordUtil.hash_password(password))
        )


def main():
    a = Admin()
    a.make_account('a', 'a')


if __name__ == "__main__":
    main()
