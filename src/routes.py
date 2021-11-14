from src import app
from src.decision_making.base import Criterium
from src.decision_making import Hierarchy
from flask import request
from http import HTTPStatus 
import dacite


@app.route('/ahp', methods=['GET'])
def ahp():
    if not request.is_json:
        return HTTPStatus.BAD_REQUEST, "json format is required"
    data = request.json
    criteria_list = map(lambda d: dacite.from_dict(data_class=Criterium, data=d), data['criteria'])
    return str(list(criteria_list))