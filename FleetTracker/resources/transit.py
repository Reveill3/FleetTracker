from flask import jsonify, request, Blueprint, redirect, url_for
from flask_restful import (Resource, Api)
from playhouse.shortcuts import model_to_dict
import models


class TransitList(Resource):

    def get(self):
        movements = models.movement.search('inTransit', 'checked')
        jsoncollection = []
        for movement in movements:
            jsondict = {
                'user': movement['fields']['Treaters'],
                'unitnumber': models.equipment.get(movement['fields']['UnitNumber'][0])['fields']['UnitNumber'],
                'Time': movement['fields']['timestamp'],
                'transferto': movement['fields']['CrewTransfer'][0],
                'transferfrom': movement['fields']['CrewFrom'][0],
                'id': movement['fields']['Movement_Id'],
                'details': movement['fields']['details'],
                'type': models.equipment.get(movement['fields']['UnitNumber'][0])['fields']['Type']
            }
            jsoncollection.append(jsondict)
        return jsonify(jsoncollection)

    def post(self):
        movements_to_cancel = request.get_json()
        for movement in movements_to_cancel:
            models.movement.update_by_field('Movement_Id', movement['id'], {'inTransit': 'not'})
            unit_number = models.equipment.get(models.movement.search('Movement_Id', movement['id'])[0]['fields']['UnitNumber'][0])['fields']['UnitNumber']
            if movement['yours']:
                models.equipment.update_by_field('UnitNumber', unit_number, {'Crew': [movement['transferfrom']]})
                models.movement.delete_by_field('Movement_Id', movement['id'])
            else:
                models.equipment.update_by_field('UnitNumber', unit_number, {'Crew': [movement['transferTo']]})


transit_api = Blueprint('resources.transit', __name__)
api = Api(transit_api)
api.add_resource(
    TransitList,
    '/api/v1/transit_list/',
    endpoint='transit_list',
)
