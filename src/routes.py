from src.decision_making.hierarchy import Criterium
from src.decision_making.ahp.ranking_method import EVMRanking, GMMRanking
from src.decision_making.ahp.comparison_matrix import MissingComparisonsError
from src.decision_making import Hierarchy
from src.decision_making import AHP
from flask import request, Blueprint
from http import HTTPStatus
import dacite


ahp_blueprint = Blueprint("ahp", __name__)

RANKING_METHOD = {
    "EVM": EVMRanking,
    "GMM": GMMRanking
}


@ahp_blueprint.route("/ahp/pairwise", methods=["GET"])
def ahp():
    if not request.is_json:
        return "json format is required", HTTPStatus.BAD_REQUEST
    data = request.json
    try:
        root_criterium = dacite.from_dict(Criterium, data["criteria"])
    except Exception as exc:
        return f"Error: {exc}", HTTPStatus.BAD_REQUEST

    try:
        ranking_method = RANKING_METHOD[request.args.get("ranking_method", "EVM").upper()]
    except ValueError as exc:
        return (
            f"Invalid ranking_method. Expected one of {list(RANKING_METHOD.keys())}, \
            got: {request.args.get('ranking_method')}",
            HTTPStatus.BAD_REQUEST,
        )
    criteria_comparisons = list(data["criteria_comparisons"])
    hierarchy_tree = Hierarchy(root_criterium)
    try:
        decision_model = AHP(
            root_criterium, criteria_comparisons, data["alternatives_comparisons"], ranking_method()
        )
        ranked = hierarchy_tree.rank_alternatives(data["alternatives"], decision_model)
    except MissingComparisonsError as exc:
        return f"{exc}", HTTPStatus.BAD_REQUEST
    except AssertionError as exc:
        return f"{exc}", HTTPStatus.BAD_REQUEST

    result = [[a, round(score, 3)] for a, score in ranked]
    return {"ranked_alternatives": result}
