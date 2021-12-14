from typing import List

from decision_making.ahp.ahp import AHP
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
    criteria_list: List[Criterium] = list(map(lambda d: dacite.from_dict(data_class=Criterium, data=d), data['criteria']))
    pairwise_comparisons = [comp[:2] + [Preference(comp[2])] for comp in data['pairwise_comparisons']]
    # filtered_alternatives = data['alternatives']
    # for need in data['needs']:
    #     if list(filter(lambda x: x.id == need[0], criteria_list))[0].higher_better:
    #         filtered_alternatives = list(filter(lambda x: x[need[0]] >= need[1], filtered_alternatives))
    #     else:
    #         filtered_alternatives = list(filter(lambda x: x[need[0]] <= need[1], filtered_alternatives))
    decision_model = AHP(
        criteria=criteria_list,
        comprehension_list=pairwise_comparisons,
        alternative_list=data['alternatives']
    )
    tree = Hierarchy(criteria_list)
    ranked = tree.rank_alternatives(data['alternatives'], decision_model)
    result = list(map(tuple, ranked))
    return {"ranked alternatives": result}