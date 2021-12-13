from typing import List
from src import app
from src.decision_making.base import Criterium, Preference
from src.decision_making import Hierarchy
from src.decision_making import AHP
from flask import request
from http import HTTPStatus 
import dacite
from dataclasses import asdict


@app.route('/ahp/pairwise', methods=['GET'])
def ahp():
    if not request.is_json:
        return HTTPStatus.BAD_REQUEST, "json format is required"
    data = request.json
    try:
        root_criterium = dacite.from_dict(Criterium, data['criteria'])
    except Exception as exc:
        return f"Error: {exc}", HTTPStatus.BAD_REQUEST
    preference_converter = lambda comp: comp[:2] + [Preference(comp[2])]
    criteria_comparisons = list(map(preference_converter, data['criteria_comparisons']))
    alternatives_comparisons = {cr_id: list(map(preference_converter, comparisons)) for cr_id, comparisons in data['alternatives_comparisons']}
    hierarchy_tree = Hierarchy(root_criterium)
    decision_model = AHP(root_criterium, criteria_comparisons, alternatives_comparisons)
    ranked = hierarchy_tree.rank_alternatives(data['alternatives'], decision_model)
    result = list(map(tuple, ranked))
    return {"ranked alternatives": result}