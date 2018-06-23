from flask import jsonify, request, Blueprint, redirect, url_for
from flask_restful import (Resource, Api)
from playhouse.shortcuts import model_to_dict
import models


class TransitList(Resource):

    def get(self):
        movements = models.Movement.select().where(models.Movement.inTransit == 'True')
        jsoncollection = []
        for movement in movements:
            movementdict = model_to_dict(movement)
            jsondict = {
                'user': movementdict['user'],
                'unitnumber': movementdict['unit_number'],
                'Time': movementdict['timestamp'].strftime('%H:%M'),
                'transferto': movementdict['crew_transfer'],
                'transferfrom': movementdict['crew_from'],
                'id': movementdict['id']
            }
            jsoncollection.append(jsondict)
        return jsonify(jsoncollection)

    def post(self):
        movements_to_cancel = request.get_json()
        for movement in movements_to_cancel:
            models.Movement.update(inTransit=False).where(models.Movement.id == movement['id']).execute()
            unit_number = models.Movement.select().where(models.Movement.id == movement['id']).get().unit_number
            if movement['yours']:
                models.Equipment.update(crew=movement['transferfrom']).where(
                    models.Equipment.unitnumber == unit_number).execute()
            else:
                models.Equipment.update(crew=movement['transferTo']).where(
                    models.Equipment.unitnumber == unit_number).execute()


transit_api = Blueprint('resources.transit', __name__)
api = Api(transit_api)
api.add_resource(
    TransitList,
    '/api/v1/transit_list/',
    endpoint='transit_list',
)
