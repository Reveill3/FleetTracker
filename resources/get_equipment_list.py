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
            hole_1_hours = ['0']
            hole_2_hours = ['0']
            hole_3_hours = ['0']
            hole_4_hours = ['0']
            hole_5_hours = ['0']
            maint_logs = equipment[3]
            move_logs = equipment[4]
            pump_hours = equipment[5]

            for maint_log in maint_logs:
                log_data = models.maintenance.get(maint_log)
                if log_data['fields']['Hole'] == '1':
                    hole_1_hours.append(log_data['fields']['pump_hours'])
                if log_data['fields']['Hole'] == '2':
                    hole_2_hours.append(log_data['fields']['pump_hours'])
                if log_data['fields']['Hole'] == '3':
                    hole_3_hours.append(log_data['fields']['pump_hours'])
                if log_data['fields']['Hole'] == '4':
                    hole_4_hours.append(log_data['fields']['pump_hours'])
                if log_data['fields']['Hole'] == '5':
                    hole_5_hours.append(log_data['fields']['pump_hours'])
                maint_messages.append([log_data['fields']['Message']])
            hole_1_life = int(pump_hours) - int(hole_1_hours[-1])
            hole_2_life = int(pump_hours) - int(hole_2_hours[-1])
            hole_3_life = int(pump_hours) - int(hole_3_hours[-1])
            hole_4_life = int(pump_hours) - int(hole_4_hours[-1])
            hole_5_life = int(pump_hours) - int(hole_5_hours[-1])
            models.equipment.update_by_field('UnitNumber',equipment[0], {'hole_1_life': hole_1_life,
                                                                        'hole_2_life': hole_2_life, 'hole_3_life': hole_3_life,
                                                                        'hole_4_life': hole_4_life, 'hole_5_life':hole_5_life})
            for move_log in move_logs:
                move_messages.append([models.movement.get(move_log)['fields']['message']])


            jsondict = {
                'unitnumber': equipment[0],
                'standby': equipment[1] == 'True',
                'station': equipment[2],
                'maintenance': maint_messages,
                'movement': move_messages,
                'hole_1_life': hole_1_life,
                'hole_2_life': hole_2_life,
                'hole_3_life': hole_3_life,
                'hole_4_life': hole_4_life,
                'hole_5_life': hole_5_life
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
