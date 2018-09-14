from flask import jsonify, Blueprint, abort
from flask_login import current_user
from flask_restful import (Resource, Api)
from playhouse.shortcuts import model_to_dict
import models
import json


class CancelTransit(Resource):

    def get(self):
        pass








cancel_api = Blueprint('resources.canceltransit', __name__)
api = Api(cancel_api)
api.add_resource(
    CancelTransit,
    '/api/v1/cancel_transit',
    endpoint='cancel_transit',
)
