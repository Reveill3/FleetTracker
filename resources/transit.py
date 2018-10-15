from flask import jsonify, request, Blueprint, redirect, url_for
from flask_restful import (Resource, Api)
from playhouse.shortcuts import model_to_dict
import models


class TransitList(Resource):

    def get(self):
        movements = models.movement.search('inTransit', 'checked')
        jsoncollection = []
        for movement in movements:
            unit = models.equipment.get(movement['fields']['UnitNumber'][0])
            equipment = (unit['fields']['UnitNumber'], unit['fields']['Standby'],
                                   unit['fields']['Station'], unit['fields']['Maintenance'], unit['fields']['Movement'], unit['fields']['pump_hours'])
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
                'user': movement['fields']['Treaters'],
                'unitnumber': unit['fields']['UnitNumber'],
                'Time': movement['fields']['timestamp'],
                'transferto': movement['fields']['CrewTransfer'][0],
                'transferfrom': movement['fields']['CrewFrom'][0],
                'id': movement['fields']['Movement_Id'],
                'details': movement['fields']['details'],
                'type': unit['fields']['Type'],
                'unit': {
                        'unitnumber': equipment[0],
                        'standby': True,
                        'station': equipment[2],
                        'maintenance': maint_messages,
                        'movement': move_messages,
                        'hole_1_life': hole_1_life,
                        'hole_2_life': hole_2_life,
                        'hole_3_life': hole_3_life,
                        'hole_4_life': hole_4_life,
                        'hole_5_life': hole_5_life}
            }
            jsoncollection.append(jsondict)
        return jsonify(jsoncollection)

    def post(self):
        movements_to_cancel = request.get_json()
        for movement in movements_to_cancel:
            models.movement.update_by_field('Movement_Id', movement['id'], {'inTransit': 'not'})
            unit = models.equipment.get(models.movement.search('Movement_Id', movement['id'])[0]['fields']['UnitNumber'][0])['fields']
            unit_type = unit['Type']
            if unit_type == 'pump' or unit_type == 'blender':
                standby = True
            else:
                standby = False
            if movement['yours']:
                models.equipment.update_by_field('UnitNumber', unit['UnitNumber'], {'Crew': [movement['transferfrom']], 'Standby': standby})
                models.movement.delete_by_field('Movement_Id', movement['id'])
            else:
                models.equipment.update_by_field('UnitNumber', unit['UnitNumber'], {'Crew': [movement['transferTo']], 'Standby': standby})



transit_api = Blueprint('resources.transit', __name__)
api = Api(transit_api)
api.add_resource(
    TransitList,
    '/api/v1/transit_list/',
    endpoint='transit_list',
)
