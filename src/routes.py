from typing import List
from src.decision_making.base import Criterium, Preference
from src.decision_making import Hierarchy
from src.decision_making import AHP
from flask import request, Blueprint
from http import HTTPStatus 
import dacite
from dataclasses import asdict


ahp_blueprint = Blueprint('ahp', __name__)


@ahp_blueprint.route('/ahp/pairwise', methods=['GET'])
def ahp():
    if not request.is_json:
        return "json format is required",  HTTPStatus.BAD_REQUEST
    data = request.json
    try:
        root_criterium = dacite.from_dict(Criterium, data['criteria'])
    except Exception as exc:
        return f"Error: {exc}", HTTPStatus.BAD_REQUEST
    preference_converter = lambda comp: comp[:2] + [Preference(comp[2])]
    criteria_comparisons = list(data['criteria_comparisons'])
    # alternatives_comparisons = {cr_id: list(comparisons) for cr_id, comparisons in data['alternatives_comparisons']}
    hierarchy_tree = Hierarchy(root_criterium)
    decision_model = AHP(root_criterium, criteria_comparisons, data['alternatives_comparisons'])
    ranked = hierarchy_tree.rank_alternatives(data['alternatives'], decision_model)
    result = [[a, round(score, 3)] for a, score in ranked]
    return {"ranked_alternatives": result}