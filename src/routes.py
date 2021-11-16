from src import app
from src.decision_making.base import Criterium, Preference
from src.decision_making import Hierarchy
from flask import request
from http import HTTPStatus 
import dacite
from src.decision_making.base.mcda import MockedModel



def validate_request(request):
    pass


@app.route('/ahp', methods=['GET'])
def ahp():
    if not request.is_json:
        return HTTPStatus.BAD_REQUEST, "json format is required"
    data = request.json
    criteria_list = list(map(lambda d: dacite.from_dict(data_class=Criterium, data=d), data['criteria']))
    pairwise_comparisons = [comp[:2] + [Preference(comp[2])] for comp in data['pairwise_comparisons']]
    decision_model = MockedModel() # TODO: AHP here
    tree = Hierarchy(criteria_list)
    ranked = tree.rank_alternatives(data['alternatives'], decision_model)
    result = list(map(tuple, ranked))
    return {"ranked alternatives": result}