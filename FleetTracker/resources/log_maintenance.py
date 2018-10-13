from flask import jsonify, request, Blueprint, redirect, url_for
from flask_restful import (Resource, Api)
from playhouse.shortcuts import model_to_dict
import models
from flask import flash
import uuid



def update_maintenance(pump_hours, hole, supervisor, grease_pressure, suction_valves,
suction_seats, discharge_valves, discharge_seats, suction_spring, discharge_spring,
packing_brass, packing_nobrass, unitnumber, crew, maintenance_type, hole_1_life,
hole_2_life, hole_3_life, hole_4_life, hole_5_life):
    """Adds an entry to maintenance given variables in request body"""
    models.maintenance.insert({'maintenance_id': uuid.uuid4().hex,
    'pump_hours': pump_hours, 'Hole': hole,
    'Treater': supervisor, 'grease_pressure': grease_pressure,
    'suction_valves': suction_valves,  'suction_seats': suction_seats,
    'discharge_valves': discharge_valves,
    'discharge_seats': discharge_seats, 'suction_spring': suction_spring,
    'discharge_spring': discharge_spring,
    'packing_brass': packing_brass, 'packing_nobrass': packing_nobrass,
    'UnitNumber': unitnumber, 'Crew': crew,
    'MaintenanceType': maintenance_type,
    'hole_1_life': hole_1_life, 'hole_2_life': hole_2_life, 'hole_3_life': hole_3_life,
    'hole_4_life': hole_4_life, 'hole_5_life': hole_5_life}, typecast=True)

class LogMaintenance(Resource):

    def post(self):
        load_data = request.get_json()
        update_maintenance(load_data['pump_hours'], load_data['hole'],
        load_data['treater'], load_data['grease_pressure'], load_data['suction_valves'],
        load_data['suction_seats'], load_data['discharge_valves'], load_data['discharge_seats'],
        load_data['suction_spring'], load_data['discharge_spring'],
        load_data['packing_brass'], load_data['packing_nobrass'],
        load_data['unitnumber'], load_data['crew'],
        load_data['maintenance_type'], load_data['hole_1_life'],
        load_data['hole_2_life'], load_data['hole_3_life'],
        load_data['hole_4_life'], load_data['hole_5_life'])
        return jsonify('Movement Logged')

log_maintenance = Blueprint('resources.log_maintenance', __name__)
api = Api(log_maintenance)
api.add_resource(
    LogMaintenance,
    '/api/v1/log_maintenance/',
    endpoint='log_maintenance',
)
