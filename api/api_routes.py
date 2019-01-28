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
