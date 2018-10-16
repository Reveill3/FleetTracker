from flask import jsonify, request, Blueprint, redirect, url_for
from flask_restful import (Resource, Api)
from playhouse.shortcuts import model_to_dict
import models

class GetTreaters(Resource):

    def get(self):
        treaters = models.treaters.get_all(view='Grid view')
        treater_names = []
        crews = []
        for treater in treaters:
            info = {
                'name': treater['fields']['Name']
            }
            treater_names.append(info)
        return jsonify(treaters=treater_names)

get_treaters = Blueprint('resources.get_treaters', __name__)
api = Api(get_treaters)
api.add_resource(
    GetTreaters,
    '/api/v1/get_treaters/',
    endpoint='get_treaters',
)
