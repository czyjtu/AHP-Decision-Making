import json
from decision_making.hierarchy import Criterium
from decision_making.ahp.ranking_method import EVMRanking, GMMRanking
from decision_making.ahp.comparison_matrix import MissingComparisonsError
from decision_making import Hierarchy
from decision_making import AHP
from flask import request, Blueprint, Flask
from http import HTTPStatus
from pprint import pprint
import sys
from decision_making.hierarchy import Hierarchy


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
        root_criterium = Criterium.from_dict(data["criteria"])
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
    return {"ranked_alternatives": ranked}


def create_app():
    app = Flask(__name__)
    app.register_blueprint(ahp_blueprint)
    return app

def main_flask():
    create_app().run(debug=True, port=8800)


def main_cmd():
    # read data 
    with open("sample_data/house_data.json", "r") as f:
        data = json.load(f)

    # build criteria tree 
    root_criterium = Criterium.from_dict(data['criteria'])

    # build decision model 
    ahp = AHP(root_criterium, data["criteria_comparisons"], data["alternatives_comparisons"], EVMRanking())

    # build hierarchy class, and get the score using decison_model
    hierarchy = Hierarchy(root_criterium)
    score = hierarchy.rank_alternatives(data["alternatives"], ahp)
    pprint(score)

def main():
    args = sys.argv[1:]
    if len(args) > 0 and args[0] == "-flask":
        main_flask()
    else:
        main_cmd()

if __name__ == '__main__':
    main()