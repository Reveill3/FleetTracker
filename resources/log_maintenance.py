from flask import jsonify, request, Blueprint, redirect, url_for
from flask_restful import (Resource, Api)
from playhouse.shortcuts import model_to_dict
import models
from flask import flash
import uuid
import math



def update_maintenance(hole, load_data, genericParts=False):
    """Adds an entry to maintenance given variables in request body"""
    vs = False
    packing = False
    number_options = ['1', '2', '3', '4', '5']
    for key in load_data:
        if 'Valve' in key or 'Seat' in key:
            if load_data[key] != False and load_data[key] != '' and load_data[key] not in number_options:
                vs = True
        if 'Packing' in key:
            if load_data[key] != False and load_data[key] != '':
                packing = True

        if load_data[key] == True:
            load_data[key] = 1
        if load_data[key] == False:
            load_data[key] = 0

    if vs:
        type = 'valves & seats'
    elif packing:
        type = 'packing'
    else:
        type = 'other'





    if genericParts:
        if hole == '0':
            models.maintenance.insert({
            'maintenance_id': uuid.uuid4().hex,
            'pump_hours': load_data['pump_hours'], 'Hole': hole,
            'Treater': load_data['treater'],
            'MaintenanceType': type,
            'four_inch_flappers': load_data['4" Flappers'],
            '6_inch_vic': load_data['6" Vic Seal'],
            'clamp_adapter': load_data['Clamp Adapter'],
            'discharge_valve_cover_with_gauge': load_data['Discharge Cover W/Gauge'],
            'discharge_flange_bolt': load_data['Discharge Flange Bolt'],
            'discharge_flange_nut':load_data['Discharge Flange Nut'],
            'discharge_o_ring':load_data['Discharge O-ring'],
            'discharge_valve_cover': load_data['Discharge Valve Cover'],
            'fmc_check_valve_kit': load_data['FMC Check Valve Kit'],
            'flange_o_ring': load_data['Flange O-ring'],
            'fluid_end_stainless': load_data['Fluid End - Stainless'],
            'fluid_end_alloy': load_data['Fluid End = Alloy'],
            'gland_nut': load_data['Gland Nut'],
            'manifold_o_ring': load_data['Manifold O-ring'],
            'pony_rod_adapter_bolts': load_data['Pony Rod Adapter Bolts'],
            'spm_check_valve_kit': load_data['SPM Check Valve Kit'],
            'spacer_adapter': load_data['Spacer/Adapter'],
            'spring_keeper': load_data['Spring Keeper'],
            'spring_keeper_pin': load_data['Spring Keeper Pin'],
            'clamp_adapter_pin': load_data['Clamp Adapter Pin'],
            'stay_rod': load_data['Stay Rod'], 'stay_rod_nut': load_data['Stay Rod Nut'],
            'suction_manifold_bolt': load_data['Suction Manifold Bolt'],
            'suction_valve_guide': load_data['Suction Valve Guide'],
            'tsi_check_valve_kit': load_data['TSI Check Valve Kit'],
            'UnitNumber': load_data['unitnumber'], 'Crew': load_data['crew'],
            'hole_1_life': load_data['hole_1_life'],
            'hole_2_life': load_data['hole_2_life'],
            'hole_3_life': load_data['hole_3_life'],
            'hole_4_life': load_data['hole_4_life'],
            'hole_5_life': load_data['hole_5_life']}, typecast=True)

        else:
            models.maintenance.insert({
            'maintenance_id': uuid.uuid4().hex,
            'pump_hours': load_data['pump_hours'], 'Hole': hole,
            'Treater': load_data['treater'],
            'MaintenanceType': type,
            'grease_pressure': load_data['grease_pressure' + hole],
            'suction_valves': load_data['Suction Valve' + hole],
            'suction_seats': load_data['Suction Seat' + hole],
            'discharge_valves': load_data['Discharge Valve' + hole],
            'discharge_seats': load_data['Discharge Seat' + hole],
            'suction_spring': load_data['Suction Spring' + hole],
            'discharge_spring': load_data['Discharge Valve Spring' + hole],
            'packing_brass': load_data["Packing(w / Brass Ring)" + hole],
            'packing_nobrass': load_data["Packing(w / o Brass Ring)" + hole],
            'plunger': load_data['Plunger' + hole],
            'clamp_plunger': load_data['Clamp Plunger' + hole],
            'four_inch_flappers': load_data['4" Flappers'],
            '6_inch_vic': load_data['6" Vic Seal'],
            'clamp_adapter': load_data['Clamp Adapter'],
            'discharge_valve_cover_with_gauge': load_data['Discharge Cover W/Gauge'],
            'discharge_flange_bolt': load_data['Discharge Flange Bolt'],
            'discharge_flange_nut':load_data['Discharge Flange Nut'],
            'discharge_o_ring':load_data['Discharge O-ring'],
            'discharge_valve_cover': load_data['Discharge Valve Cover'],
            'fmc_check_valve_kit': load_data['FMC Check Valve Kit'],
            'flange_o_ring': load_data['Flange O-ring'],
            'fluid_end_stainless': load_data['Fluid End - Stainless'],
            'fluid_end_alloy': load_data['Fluid End = Alloy'],
            'gland_nut': load_data['Gland Nut'],
            'manifold_o_ring': load_data['Manifold O-ring'],
            'pony_rod_adapter_bolts': load_data['Pony Rod Adapter Bolts'],
            'spm_check_valve_kit': load_data['SPM Check Valve Kit'],
            'spacer_adapter': load_data['Spacer/Adapter'],
            'spring_keeper': load_data['Spring Keeper'],
            'spring_keeper_pin': load_data['Spring Keeper Pin'],
            'clamp_adapter_pin': load_data['Clamp Adapter Pin'],
            'stay_rod': load_data['Stay Rod'], 'stay_rod_nut': load_data['Stay Rod Nut'],
            'suction_manifold_bolt': load_data['Suction Manifold Bolt'],
            'suction_valve_guide': load_data['Suction Valve Guide'],
            'tsi_check_valve_kit': load_data['TSI Check Valve Kit'],
            'UnitNumber': load_data['unitnumber'], 'Crew': load_data['crew'],
            'hole_1_life': load_data['hole_1_life'],
            'hole_2_life': load_data['hole_2_life'],
            'hole_3_life': load_data['hole_3_life'],
            'hole_4_life': load_data['hole_4_life'],
            'hole_5_life': load_data['hole_5_life']}, typecast=True)

    else:
        models.maintenance.insert({
        'maintenance_id': uuid.uuid4().hex,
        'pump_hours': load_data['pump_hours'], 'Hole': hole,
        'MaintenanceType': type,
        'Treater': load_data['treater'],
        'UnitNumber': load_data['unitnumber'],
        'Crew': load_data['crew'],
        'grease_pressure': load_data['grease_pressure' + hole],
        'suction_valves': load_data['Suction Valve' + hole],
        'suction_seats': load_data['Suction Seat' + hole],
        'discharge_valves': load_data['Discharge Valve' + hole],
        'discharge_seats': load_data['Discharge Seat' + hole],
        'suction_spring': load_data['Suction Spring' + hole],
        'discharge_spring': load_data['Discharge Valve Spring' + hole],
        'packing_brass': load_data["Packing(w / Brass Ring)" + hole],
        'packing_nobrass': load_data["Packing(w / o Brass Ring)" + hole],
        'plunger': load_data['Plunger' + hole],
        'clamp_plunger': load_data['Clamp Plunger' + hole],
        'hole_1_life': load_data['hole_1_life'],
        'hole_2_life': load_data['hole_2_life'],
        'hole_3_life': load_data['hole_3_life'],
        'hole_4_life': load_data['hole_4_life'],
        'hole_5_life': load_data['hole_5_life']}, typecast=True)



class LogMaintenance(Resource):

    def post(self):
        load_data = request.get_json()
        if len(load_data['toUpdate']) > 0:
            for index, hole in enumerate(load_data['toUpdate']):
                if index == 0:
                    update_maintenance(hole, load_data, genericParts=True)
                else:
                    update_maintenance(hole, load_data)
        else:
            update_maintenance(str(0) , load_data, genericParts=True)

        return jsonify('Movement Logged')

log_maintenance = Blueprint('resources.log_maintenance', __name__)
api = Api(log_maintenance)
api.add_resource(
    LogMaintenance,
    '/api/v1/log_maintenance/',
    endpoint='log_maintenance',
)
