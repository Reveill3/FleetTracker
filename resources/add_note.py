from flask import jsonify, request, Blueprint, redirect, url_for
from flask_restful import (Resource, Api)
from playhouse.shortcuts import model_to_dict
import models

class AddNote(Resource):

    def post(self):
        load_data = request.get_json()
        treater = models.treaters.search('Name', load_data['supervisor'])[0]['id']
        unitnumber = models.equipment.search('UnitNumber', load_data['unitnumber'])[0]['id']
        title = load_data['title']
        details = load_data['details']
        print(load_data['supervisor'])
        models.notes.insert({
        'Title': title,
        'Details': details,
        'Unit Number': load_data['unitnumber'],
        'Supervisor Name': load_data['supervisor'],
        }, typecast=True)
        return jsonify('Update Success')

add_note = Blueprint('resources.add_note', __name__)
api = Api(add_note)
api.add_resource(
    AddNote,
    '/api/v1/add_note/',
    endpoint='add_note',
)
