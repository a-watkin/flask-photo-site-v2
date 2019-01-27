import os
import sqlite3


class Database(object):
    def __init__(self):
        self.db_name = 'eigi-data.db'

    @classmethod
    def get_placeholders(cls, num):
        return ','.join(['?' for x in list(range(num))])

    def delete_database(self):
        if self.db_name in os.listdir():
            try:
                os.remove(self.db_name)
                self.db_name = None
                return True
            except OSError as e:
                print('Problem: ', e)
        else:
            print('Database not found')
            return False

    def make_sanitized_query(self, query_string, data=None):
        # print('make_sanitized_query')
        # print(query_string)
        # print(data)

        try:
            with sqlite3.connect(os.path.join(self.db_name)) as connection:
                c = connection.cursor()
                return [x for x in c.execute(query_string, data)]
        except Exception as e:
            print('make_sanitized_query ', e)

    def make_query(self, query_string):
        print(query_string)
        with sqlite3.connect(os.path.join(self.db_name)) as connection:
            c = connection.cursor()
            return [x for x in c.execute(query_string)]

    def get_row(self, table_name, id_name, id_value):
        try:
            q_data = None
            with sqlite3.connect(self.db_name) as connection:
                c = connection.cursor()
                c.row_factory = sqlite3.Row
                q_data = c.execute(
                    '''
                    SELECT * FROM {} WHERE {} = "{}"
                    '''.format(
                        table_name, id_name, id_value
                    )
                )

            return [dict(ix) for ix in q_data]

        except Exception as e:
            print('problem getting row ', e)

    def get_rows(self, table_name):
        q_data = None
        with sqlite3.connect(self.db_name) as connection:
            c = connection.cursor()
            c.row_factory = sqlite3.Row
            q_data = c.execute(
                '''
                SELECT * FROM {}
                '''.format(table_name))

        return [dict(ix) for ix in q_data]

    def get_query_as_list(self, query_string):
        # print('get_query_as_list called', query_string)
        q_data = None
        with sqlite3.connect(self.db_name) as connection:
            c = connection.cursor()
            c.row_factory = sqlite3.Row
            q_data = c.execute(query_string)

        return [dict(ix) for ix in q_data]


if __name__ == "__main__":
    db = Database()
