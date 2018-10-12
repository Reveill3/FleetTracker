from flask import jsonify, request, Blueprint, redirect, url_for
from flask_restful import (Resource, Api)
from playhouse.shortcuts import model_to_dict
import models

class GetEquipmentList(Resource):

    def post(self):
        load_data = request.get_json()
        equipment_list = models.create_list(load_data['crew'], load_data['type'])
        jsoncollection = []
        for equipment in equipment_list:
            maint_messages = []
            move_messages = []
            maint_logs = equipment[3]
            move_logs = equipment[4]
            for maint_log in maint_logs:
                maint_messages.append([models.maintenance.get(maint_log)['fields']['Message']])
            for move_log in move_logs:
                move_messages.append([models.movement.get(move_log)['fields']['message']])

            jsondict = {
                'unitnumber': equipment[0],
                'standby': equipment[1] == 'True',
                'station': equipment[2],
                'maintenance': maint_messages,
                'movement': move_messages
            }
            jsoncollection.append(jsondict)
        sorted_by_station = sorted(jsoncollection, key=lambda k: k['station'])
        return jsonify(equipment=sorted_by_station, type=load_data['type'])

get_api = Blueprint('resources.get_equipment', __name__)
api = Api(get_api)
api.add_resource(
    GetEquipmentList,
    '/api/v1/get_equipment/',
    endpoint='get_equipment',
)
