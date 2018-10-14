from flask import jsonify, request, Blueprint, redirect, url_for
from flask_restful import (Resource, Api)
from playhouse.shortcuts import model_to_dict
import models


class UpdatePumpHours(Resource):

    def post(self):
        load_data = request.get_json()
        for key, value in load_data.items():
            models.equipment.update_by_field(
                'UnitNumber', key, {'pump_hours': value}, typecast=True)


update_pump_hours = Blueprint('resources.update_pump_hours',  __name__)
api = Api(update_pump_hours)
api.add_resource(
    UpdatePumpHours,
    '/api/v1/update_pump_hours/',
    endpoint='update_pump_hours',
)