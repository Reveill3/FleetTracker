from flask import jsonify, request, Blueprint, redirect, url_for
from flask_restful import (Resource, Api)
from playhouse.shortcuts import model_to_dict
import models
from flask import flash
import uuid



def move(equipment_field, crew_field, supervisor, message, transfer_from):
    """Moves a piece of equipment to specified crew in database.
    Changes 'crew' column in database to specified field"""
    models.equipment.update_by_field('UnitNumber', equipment_field, {'Crew': ['rec0Q6Z9R2isNg34V']})
    models.movement.insert({'Movement_Id': uuid.uuid4().hex, 'message': '{} has moved {} to {} crew'.format(
        supervisor, equipment_field, crew_field), 'inTransit': 'checked', 'UnitNumber': equipment_field,
                           'CrewTransfer': crew_field, 'CrewFrom': transfer_from, 'details': message, 'Treaters': supervisor}, typecast=True)

class MoveEquipment(Resource):

    def post(self):
        load_data = request.get_json()
        print(load_data['equipment'])
        move(load_data['equipment'], load_data['crew'], load_data['treater'], load_data['reason'], load_data['crewFrom'])
        return jsonify('Movement Logged')

move_equipment = Blueprint('resources.move_equipment', __name__)
api = Api(move_equipment)
api.add_resource(
    MoveEquipment,
    '/api/v1/move_equipment/',
    endpoint='move_equipment',
)
