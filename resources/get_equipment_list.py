from flask import jsonify, request, Blueprint, redirect, url_for
from flask_restful import (Resource, Api)
from playhouse.shortcuts import model_to_dict
import models

class GetEquipmentList(Resource):

    def post(self):
        load_data = request.get_json()
        equipment_list = models.create_list(load_data['crew'], load_data['type'])
        jsoncollection = []
        max_list = []
        total_notes = models.notes.get_all(fields=['Note Number'])
        for note in total_notes:
            max_list.append(note['fields']['Note Number'])
        max_note_number = max(max_list)
        for equipment in equipment_list:
            maint_messages = []
            move_messages = []
            notes_note = []
            hole_1_hours = ['0']
            hole_2_hours = ['0']
            hole_3_hours = ['0']
            hole_4_hours = ['0']
            hole_5_hours = ['0']
            maint_logs = equipment[3]
            move_logs = equipment[4]
            pump_hours = equipment[5]
            notes = equipment[6]
            for note in notes:
                note_data = models.notes.get(note)
                treater = models.treaters.get(note_data['fields']['Supervisor Name'][0])['fields']['Name']
                notes_note.append({
                    'totalNotes': max_note_number,
                    'noteNum': note_data['fields']['Note Number'],
                    'id': note_data['id'],
                    'title': note_data['fields']['Title'],
                    'details': note_data['fields']['Details'],
                    'treater': treater
                })
            for maint_log in maint_logs:
                log_data = models.maintenance.get(maint_log)
                if log_data['fields']['Hole'] == '1' and log_data['fields']['MaintenanceType'] == 'valves & seats':
                    hole_1_hours.append(log_data['fields']['pump_hours'])
                if log_data['fields']['Hole'] == '2' and log_data['fields']['MaintenanceType'] == 'valves & seats':
                    hole_2_hours.append(log_data['fields']['pump_hours'])
                if log_data['fields']['Hole'] == '3' and log_data['fields']['MaintenanceType'] == 'valves & seats':
                    hole_3_hours.append(log_data['fields']['pump_hours'])
                if log_data['fields']['Hole'] == '4' and log_data['fields']['MaintenanceType'] == 'valves & seats':
                    hole_4_hours.append(log_data['fields']['pump_hours'])
                if log_data['fields']['Hole'] == '5' and log_data['fields']['MaintenanceType'] == 'valves & seats':
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
                'maintenance': maint_messages[-3],
                'movement': move_messages,
                'pump_hours': pump_hours,
                'hole_1_life': hole_1_life,
                'hole_2_life': hole_2_life,
                'hole_3_life': hole_3_life,
                'hole_4_life': hole_4_life,
                'hole_5_life': hole_5_life,
                'previous_hours': {'hole_1': int(hole_1_hours[-1]),
                                    'hole_2': int(hole_2_hours[-1]),
                                    'hole_3': int(hole_3_hours[-1]),
                                    'hole_4': int(hole_4_hours[-1]),
                                    'hole_5': int(hole_5_hours[-1]),
                                    },
                'notes': notes_note
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
