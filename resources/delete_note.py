from flask import jsonify, request, Blueprint, redirect, url_for
from flask_restful import (Resource, Api)
from playhouse.shortcuts import model_to_dict
import models

class DeleteNote(Resource):

    def post(self):
        load_data = request.get_json()
        to_delete = models.notes.search('Unit Number', load_data['unitnumber'])[0]
        models.notes.delete(to_delete['id'])
        return jsonify('Update Success')

delete_note = Blueprint('resources.delete_note', __name__)
api = Api(delete_note)
api.add_resource(
    DeleteNote,
    '/api/v1/delete_note/',
    endpoint='delete_note',
)
