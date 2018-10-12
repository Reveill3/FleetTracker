from flask import jsonify, request, Blueprint, redirect, url_for
from flask_restful import (Resource, Api)
from playhouse.shortcuts import model_to_dict
import models

class UpdateLayout(Resource):

    def post(self):
        load_data = request.get_json()
        inline_list = load_data['inline']
        standby_list = load_data['standby']
        for equipment in inline_list:
            models.equipment.update_by_field('UnitNumber', equipment['unitnumber'],
            {'Standby': str(equipment['standby']).title(),
            'Station': inline_list.index(equipment) + 1})
        for equipment in standby_list:
            models.equipment.update_by_field('UnitNumber', equipment['unitnumber'],
                        {'Standby': str(equipment['standby']).title(),
                        'Station': standby_list.index(equipment) + 1 + len(inline_list)})
        return jsonify('Update Success')

update_layout = Blueprint('resources.update_layout', __name__)
api = Api(update_layout)
api.add_resource(
    UpdateLayout,
    '/api/v1/update_layout/',
    endpoint='update_layout',
)
