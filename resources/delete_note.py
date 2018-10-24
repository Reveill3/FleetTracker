from flask import jsonify, request, Blueprint, redirect, url_for
from flask_restful import (Resource, Api)
from playhouse.shortcuts import model_to_dict
import models

class DeleteNote(Resource):

    def post(self):
        load_data = request.get_json()
        if load_data['recId'] == 'new':
            to_delete = models.notes.search('Note Number', load_data['noteNum'])[0]['id']
            models.notes.delete(to_delete)
        else:
            models.notes.delete(load_data['recId'])

        return jsonify('Update Success')

delete_note = Blueprint('resources.delete_note', __name__)
api = Api(delete_note)
api.add_resource(
    DeleteNote,
    '/api/v1/delete_note/',
    endpoint='delete_note',
)
