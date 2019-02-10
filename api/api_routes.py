# flask imports
from flask import Blueprint, jsonify, request, render_template, redirect, url_for, flash, session
# my modules common
from common.utils import login_required
# registering the blueprint for this package
api_blueprint = Blueprint('api', __name__)


@api_blueprint.route('/uploaded/title', methods=['GET', 'POST'])
@login_required
def update_title():
    d = request.get_json()
    title = d['title'].strip()
    title = name_util.make_encoded(title)

    if up.update_title(d['photoId'], title):
        return json.dumps({'success': True}), 200, {'ContentType': 'application/json'}
    else:
        return json.dumps({'success': False}), 500, {'ContentType': 'application/json'}


@api_blueprint.route('/api/select/album')
@login_required
def upload_select_album():
    return render_template('upload_select_album.html'), 200


@api_blueprint.route('/api/upload/photostream', methods=['GET', 'POST'])
@login_required
def to_photostream():
    # print('hello from to_photostream')
    data = request.get_json()
    up.add_to_photostream(data['photos'])
    return json.dumps({'success': False}), 200, {'ContentType': 'application/json'}


@api_blueprint.route('/api/create/album', methods=['GET', 'POST'])
@login_required
def to_new_album():
    # print('hello from to_new_album')
    if request.method == 'GET':
        return render_template('upload_new_album.html'), 200

    if request.method == 'POST':
        album_title = request.form['title']
        album_description = request.form['description']

        if a.get_album_by_name(album_title):
            new_album_data = {
                'album_title': album_title,
                'album_description': album_description
            }

            flash(
                'An album with this name already exists. Please enter a different name.')

            return render_template('create_album.html', data=new_album_data), 200

        else:

            album_id = a.create_album(
                '28035310@N00', album_title, album_description)

            # use album_id to add all uploaded photos to the album
            up.add_all_to_album(album_id)

            album_data = a.get_album(album_id)

            return redirect('/albums/{}'.format(album_id)), 302


@api_blueprint.route('/api/uploaded/')
@login_required
def get_uploaded_photos():
    print('hitting up the server firefox?')

    json_data = up.get_uploaded_photos()
    # json_data = up.get_uploaded_photos_test()
    print(json_data)
    return jsonify(json_data)


@api_blueprint.route('/api/photos/')
def get_photos():
    # print('\nHello from get_photos\n')
    # print(20 * '\n', 'ENTERED')
    args = request.args.to_dict()

    photo_data = None
    # print(args)

    if len(args) > 0:

        if 'offset' in args.keys() and 'limit' not in args.keys():
            if int(args['offset']) <= 0:
                args['offset'] = 0
            # gotta make this an int
            photo_data = p.get_photos_in_range(20, int(args['offset']))

            print(photo_data)

            json_data = photo_data

            # print('args are ', args)
            json_data = show_uplaoded(json_data)
            return render_template('photos.html', json_data=json_data), 200
        elif 'offset' not in args.keys() and 'limit' in args.keys():
            # print(9 * '\n')
            # default offset is 0
            photo_data = p.get_photos_in_range(int(args['limit']))
            json_data = photo_data

            json_data = show_uplaoded(json_data)
            return render_template('photos.html', json_data=json_data), 200

        else:
            """
            both offset and limit are present
            """
            if int(args['offset']) <= 0:
                args['offset'] = 0

            if int(args['limit']) <= 0:
                args['offset'] = 0

            photo_data = p.get_photos_in_range(
                int(args['limit']), int(args['offset'])
            )

            json_data = photo_data

            json_data = show_uplaoded(json_data)
            return render_template('photos.html', json_data=json_data), 200

    else:
        """
        No arguments
        """
        photo_data = p.get_photos_in_range()
        json_data = photo_data

        # print('\n', session and len(up.get_uploaded_photos()['photos']) > 0)
        # if session and len(up.get_uploaded_photos()['photos']) > 0:
        #     print('\n session present \n')
        #     json_data['show_session'] = True

        # print(json_data)
        # print(10*'\n')

        json_data = show_uplaoded(json_data)
        return render_template('photos.html', json_data=json_data), 200


@api_blueprint.route('/api/getalbums', methods=['GET', 'POST'])
@login_required
def get_albums_json():
    print('get_albums_json called')
    args = request.args.to_dict()

    # print(args)
    if request.method == 'GET':
        if len(args) > 0:

            if 'offset' in args.keys() and 'limit' not in args.keys():
                if int(args['offset']) <= 0:
                    args['offset'] = 0
                # gotta make this an int
                album_data = a.get_albums_in_range(20, int(args['offset']))
                json_data = album_data
                return jsonify(json_data)

        else:
            args['offset'] = 0
            album_data = a.get_albums_in_range(20, int(args['offset']))
            json_data = album_data
            return jsonify(album_data)

    if request.method == 'POST':
        print('called api/getalbum with a post request')
        print('test', request.get_json())

        data = request.get_json()

        album_id = data['albumId'][0]

        # add all the uplaoded photos to the album
        up.add_all_to_album(album_id)

        return redirect("/albums/{}".format(album_id), code=302)

        # add_all_to_album

        #     data = request.get_json()
        #     a.add_photos_to_album(data['albumId'], data['photos'])

        #     return redirect("/albums/{}".format(data['albumId']), code=302)


@api_blueprint.route('/api/getphotos', methods=['GET', 'POST'])
@login_required
def get_photos_json():
    # print()
    # print('hello from get_photos_json')
    # print()
    args = request.args.to_dict()

    # print(args)
    if request.method == 'GET':
        if len(args) > 0:

            if 'offset' in args.keys() and 'limit' not in args.keys():
                if int(args['offset']) <= 0:
                    args['offset'] = 0
                # gotta make this an int
                photo_data = p.get_photos_in_range(20, int(args['offset']))
                json_data = photo_data

                # print('args are ', args)

                json_data = photo_data
                return jsonify(json_data)

        else:
            args['offset'] = 0
            photo_data = p.get_photos_in_range(20, int(args['offset']))
            json_data = photo_data
            return jsonify(json_data)

    if request.method == 'POST':

        print('hello from get_photos_json, data passed is ', request.get_json())

        data = request.get_json()
        a.add_photos_to_album(data['albumId'], data['photos'])

        return redirect("/albums/{}".format(data['albumId']), code=302)


@api_blueprint.route('/api/photos/<int:photo_id>', methods=['GET'])
def get_photo(photo_id):
    # print('\nHello from get_photo\n')
    photo_data = p.get_photo(photo_id)
    json_data = photo_data
    # json_data = dict(photo_data['photos'])2
    # print(json_data)
    return render_template('photo.html', json_data=json_data), 200


@api_blueprint.route('/api/add/tags', methods=['GET', 'POST'])
@login_required
def add_uploaded_tags():
    """
    gets data from react
    """
    tag_data = request.get_json()
    print('tags from react ', tag_data)
    # tags are a string when they come in here,
    # they need to be split
    tags = tag_data['tagValues'].split(',')

    for i in range(len(tags)):
        # remove whitespace from front and back of element
        tags[i] = tags[i].strip()
        # make it url safe
        tags[i] = url_encode_tag(tags[i])

    print(tags)

    print('tag_data', tag_data)
    resp = t.add_tags_to_photo(tag_data['photoId'], tags)
    print(resp)
    if resp:
        return json.dumps({'success': True}), 200, {'ContentType': 'application/json'}
    else:
        return json.dumps({'success': False}), 500, {'ContentType': 'application/json'}


@api_blueprint.route('/api/tag/photos', methods=['GET', 'POST'])
def get_tag_photos():
    args = request.args.to_dict()

    print('get_tag_photos args, ', args)

    if 'offset' in args.keys():
        offset = int(args['offset'])

        if offset < 0:
            offset = 0

        tag_photos_data = t.get_tag_photos_in_range(
            args['tag_name'], 20, offset)

        if offset >= tag_photos_data['tag_info']['number_of_photos']:
            offset = tag_photos_data['tag_info']['number_of_photos']
            pass

        return render_template('tag_photos.html', json_data=tag_photos_data)

    tag_photos_data = t.get_tag_photos_in_range(args['tag_name'])
    return render_template('tag_photos.html', json_data=tag_photos_data)


@api_blueprint.route('/api/get/phototags', methods=['GET', 'POST'])
@login_required
def get_photo_tag_data():
    if request.method == 'GET':
        args = request.args.to_dict()
        photo_data = p.get_photo(args['photo_id'])
        return jsonify(photo_data)
    else:
        data = request.get_json()
        print(data)
        # remove tags here
        print(data['photoId'], data['selectedTags'])

        # for i in range(len(data['selectedTags'])):
        #     data['selectedTags'][i] = check_chars(data['selectedTags'][i])

        t.remove_tags_from_photo(data['photoId'], data['selectedTags'])
        return json.dumps({'success': True}), 200, {'ContentType': 'application/json'}


@api_blueprint.route('/api/albumphotos', methods=['GET', 'POST'])
@login_required
def get_album_photos_json():
    """
    Used to pass data to React.
    """
    args = request.args.to_dict()
    # print(args)
    if request.method == 'GET':
        if len(args) > 0:

            if 'limit' not in args.keys():
                args['limit'] = 20

            if 'offset' not in args.keys():
                args['offset'] = 0

            album_data = a.get_album_photos_in_range(
                args['album_id'],
                args['limit'],
                args['offset']
            )
            json_data = album_data
            return jsonify(json_data)

    if request.method == 'POST':
        # print('test', request.get_json())
        data = request.get_json()
        a.remove_photos_from_album(data['albumId'], data['photos'])
        return redirect("/albums/{}".format(data['albumId']), code=302)


@api_blueprint.route('/api/album/photos', methods=['GET', 'POST'])
def get_album_photos_in_pages():
    args = request.args.to_dict()

    print(args)

    if 'offset' in args.keys():
        offset = int(args['offset'])

        if offset <= 0:
            # pass
            offset = 0

        # guards against an offset greater than the number of photos
        if offset >= a.count_photos_in_album(args['album_id']):
            # ok if you want it to return to the start of the pages
            # offset = 0
            pass

        # else:
        album_photos = a.get_album_photos_in_range(
            args['album_id'], 20, offset)
        return render_template('album.html', json_data=album_photos)

    album_photos = a.get_album_photos_in_range(args['tag_name'])
    return render_template('album.html', json_data=album_photos)


@api_blueprint.route('/discard/photo', methods=['GET', 'POST'])
@login_required
def discard_photo():
    photo_id = request.get_json()
    # print('getting here?')
    # print(photo_id)
    # print(photo_id)

    result = up.discard_photo(photo_id['photoId'])
    # print(result)

    if up.discard_photo(photo_id['photoId']):
        return json.dumps({'success': True}), 200, {'ContentType': 'application/json'}
    else:
        return json.dumps({'success': False}), 500, {'ContentType': 'application/json'}
