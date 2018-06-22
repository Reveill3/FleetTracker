from flask import jsonify, Blueprint
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
                'unitnumber': movementdict['unitnumber'],
                'Time': movementdict['timestamp'].strftime('%H:%M'),
                'transferto': movementdict['crewtransfer'],
            }
            jsoncollection.append(jsondict)
        return jsonify(jsoncollection)


transit_api = Blueprint('resources.transit', __name__)
api = Api(transit_api)
api.add_resource(
    TransitList,
    '/api/v1/transit_list/',
    endpoint='transit_list',
)

192