import os
import json
import datetime

from flask import session

import sys

try:
    from database_interface import Database
    from tag import Tag
    import common.name_util
    from common.exif_util import ExifUtil

except Exception as e:
    # print('import problem, ', e)
    sys.path.append('/home/a/projects/flask-photo-site')
    from common.db_interface import Database
    from common.password_util import PasswordUtil


# from exif_util import ExifUtil


class UploadedPhotos(object):
    """
    Handles a table of photos connected to a user.

    These represent recently uploaded files that have not had values set for things like title, tags etc.

    They will be stored in the table until they are saved.
    """

    def __init__(self):
        self.db = Database()
        # self.user_id = '28035310@N00'
        # self.tag = Tag()

    def show_uploaded(self):
        """
        Return true is the uploaded_photo table is not empty.
        """
        uploaded_photos = self.db.get_query_as_list(
            '''
            select * from upload_photo
            '''
        )

        if uploaded_photos:
            return True
        return False

    def save_photo(self, photo_id, date_uploaded, original, large_square, exif_data, date_taken):
        # date_taken = None
        exif_id = str(int(uuid.uuid4()))[0:10]

        # insert exif data
        self.db.insert_data(
            exif_id=exif_id,
            exif_data=exif_data,
            photo_id=photo_id,
            table='exif'
        )

        # write to the uploaded_photo table
        query_string = '''
        insert into upload_photo(photo_id, user_id)
        values('{}', '{}')
        '''.format(photo_id, self.user_id)

        # print(query_string)

        self.db.make_query(query_string)

        # write to the photo table
        self.db.make_query(
            '''
            insert into photo(photo_id, user_id, views, date_uploaded, date_taken)
            values({},'{}', {}, '{}', '{}')
            '''.format(int(photo_id), self.user_id, 0, date_uploaded, str(date_taken))
        )

        # write to images
        self.db.make_query(
            '''
            insert into images(photo_id, original, large_square)
            values({},'{}','{}')
            '''.format(int(photo_id), original, large_square)
        )

        # should probably get and store exif data

    def get_photos_in_range(self, limit=20, offset=0):
        """
        Returns the latest 10 photos.

        Offset is where you want to start from, so 0 would be from the most recent.
        10 from the tenth most recent etc.
        """
        q_data = None
        with sqlite3.connect(self.db.db_name) as connection:
            c = connection.cursor()

            c.row_factory = sqlite3.Row

            query_string = (
                '''select photo_id, views, photo_title, date_uploaded, date_taken, images.original, images.large_square from photo
                join images using(photo_id)
                order by date_uploaded
                desc limit {} offset {}'''
            ).format(limit, offset)

            q_data = c.execute(query_string)

        rtn_dict = {
            'limit': limit,
            'offset': offset,
            'photos': []
        }

        """
        I think it may actually be better to layout what fields you want here.

        And maybe include all sizes.
        """

        data = [dict(ix) for ix in q_data]

        a_dict = {}
        count = 0
        for d in data:
            a_dict[count] = d
            count += 1

        rtn_dict = {'photos': a_dict}

        rtn_dict['limit'] = limit
        rtn_dict['offset'] = offset

        return rtn_dict

    def get_uploaded_photos(self):
        # photo_id
        # from image the original size
        q_data = None
        with sqlite3.connect(self.db.db_name) as connection:
            c = connection.cursor()

            c.row_factory = sqlite3.Row

            query_string = (
                '''
                select * from upload_photo
                join photo on(photo.photo_id=upload_photo.photo_id)
                join images on(images.photo_id=upload_photo.photo_id)
                '''
            )

            q_data = c.execute(query_string)

        data = [dict(ix) for ix in q_data]

        print(data)

        # print((self.tag.get_photo_tags(data[0]['photo_id'])))

        # fix this later so that it doesn't suck
        for photo in data:
            # print(self.tag.get_photo_tags(photo['photo_id']))
            photo['tags'] = []
            if photo['photo_title']:
                photo['photo_title'] = name_util.make_decoded(
                    photo['photo_title'])
            for tag in self.tag.get_photo_tags(photo['photo_id']):
                for key, value in tag.items():
                    print()
                    print('key', key, 'value', value)
                    if key == 'human_readable_tag':
                        print('wtf', value, photo['tags'])
                        photo['tags'].append(value)

        a_dict = {}
        count = 0
        for d in data:
            a_dict[count] = d
            count += 1

        rtn_dict = {'photos': a_dict}

        return rtn_dict

    def get_uploaded_photos_test(self):
        # photo_id
        # from image the original size
        q_data = None
        with sqlite3.connect(self.db.db_name) as connection:
            c = connection.cursor()

            c.row_factory = sqlite3.Row

            query_string = (
                '''
                select * from upload_photo
                join photo on(photo.photo_id=upload_photo.photo_id)
                join images on(images.photo_id=upload_photo.photo_id)
                '''
            )

            q_data = c.execute(query_string)

        data = [dict(ix) for ix in q_data]

        print(data)

        return {'photos': data}

    def discard_photo(self, photo_id):
        """
        Removes the specified photo from photo, upload_photo tables.
        Also deletes the files from the disk.

        Returns True if the photo is not in the upload_photo table.
        """
        # delete the files from the disk, you need to know the path to do this
        # which you should get from images
        images_data = self.db.make_query(
            '''
            select * from images where photo_id = {}
            '''.format(photo_id)
        )

        if len(images_data) > 0:
            print(images_data[0][0:len(images_data[0]) - 1])

            current_path = os.getcwd()
            photos_on_disk = []
            # the last returned element is the photo_id so to avoid that
            # I took the slice of everything up to that
            for image in images_data[0][0:len(images_data[0]) - 1]:
                if image is not None:
                    photos_on_disk.append(current_path + image)

            for photo in photos_on_disk:
                try:
                    os.remove(photo)
                except Exception as e:
                    print('Problem removing file ', e)
        else:
            print('no data')

        # remove photo from table photo
        self.db.make_query(
            '''
            delete from photo where photo_id = {}
            '''.format(photo_id)
        )

        # images should cascade delete, but check
        # Seems so

        # remove from upload_photo table
        self.db.make_query(
            '''
            delete from upload_photo where photo_id = {}
            '''.format(photo_id)
        )

        upload_photos = self.get_uploaded_photos()
        # print(upload_photos['photos'])

        for photo in upload_photos['photos']:
            # print()
            # print(upload_photos['photos'][photo])

            if photo_id in upload_photos['photos'][photo]:
                print('PROBLEM?')
                return False

        return True

        # IMPORTANT!
        # you should test this later after implementing adding tags to uploaded photos
        # remove from tags? i don't think you need to? you can have orphaned tags

    def update_title(self, photo_id, new_title):
        self.db.make_query(
            '''
            update photo
            set photo_title = '{}'
            where photo_id = {}
            '''.format(new_title, photo_id)
        )

        # check title has been updated
        data = self.db.make_query(
            '''
            select * from photo where photo_id = {}
            '''.format(photo_id)
        )

        if len(data) > 0:
            if data[0][3] == new_title:
                return True

        return False

    def add_to_photostream(self, data):
        print('PROBLEM DATA ', data)
        # get the photo_id for eatch photo
        for photo in data.values():
            # set the date_posted to the current datetime
            date_posted = datetime.datetime.now()
            # get the photo_id
            print(photo['photo_id'], date_posted)

            if photo['photo_title'] is None:
                check_title = self.db.make_query(
                    '''
                    select photo_title from photo where photo_id = {}
                    '''.format(photo['photo_id'])
                )

                if len(check_title) < 1:

                    print('here be problems?')
                    self.db.make_query(
                        '''
                        update photo
                        set photo_title = ''
                        where photo_id = {}
                        '''.format(photo['photo_id'])
                    )

            # update the date_posted column in the table photo
            self.db.make_query(
                '''
                update photo
                set date_posted = '{}'
                where photo_id = {}
                '''.format(date_posted, photo['photo_id'])
            )

            test_data = self.db.make_query(
                '''
                select date_posted from photo
                where photo_id = {}
                '''.format(photo['photo_id'])
            )

            if test_data:
                # remove the photo from the table upload_photo
                self.db.make_query(
                    '''
                    delete from upload_photo
                    where photo_id = {}
                    '''.format(photo['photo_id'])
                )

    def add_all_to_album(self, album_id):
        # get all uploaded photos
        uploaded_photos = self.db.make_query(
            '''
            select * from upload_photo
            '''
        )

        print(uploaded_photos)

        for photo in uploaded_photos:
            photo_id = photo[0]

            date_posted = datetime.datetime.now()
            # set published datetime
            self.db.make_query(
                '''
                update photo
                set date_posted = "{}"
                where photo_id = {}
                '''.format(date_posted, photo_id)
            )

            print(photo_id)
            # db.insert_data(
            #     table='tag',
            #     tag_name=new_tag,
            #     user_id='28035310@N00'
            # )

            self.db.make_query(
                '''
                insert into photo_album (photo_id, album_id)
                values ('{}', '{}')
                '''.format(photo_id, album_id)
            )

            # get photo count for album
            photo_count = self.db.make_query(
                '''
                select photos from album where album_id = '{}'
                '''.format(album_id)
            )

            print(photo_count)
            photo_count = int(photo_count[0][0]) + 1

            self.db.make_query(
                '''
                update album
                set photos = {}
                where album_id = '{}'
                '''.format(photo_count, album_id)
            )

        # DANGER!
        self.db.make_query(
            '''
            delete from upload_photo
            '''
        )


def main():
    up = UploadedPhotos()

    print(up.show_uplaoded())


if __name__ == "__main__":
    main()
