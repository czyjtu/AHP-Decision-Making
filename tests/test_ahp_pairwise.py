import pytest 
from src import create_app
from itertools import combinations


def merge_tuples(tup):
    return list(tup[0]) + [tup[1]]

@pytest.fixture 
def client():
    app = create_app()
    with app.test_client() as client:
        yield client 


@pytest.fixture 
def criteria_names():
    return ["price", "size", "transportation", "neighbourhood", "age", "yard", "facilities", "conditions"]


@pytest.fixture 
def alternatives_names():
    return ["house 1", "house 2", "house 3"]


@pytest.fixture 
def criteria(criteria_names):
    return {
        "id": "score",
        "sub_criteria": [{"id": name} for name in criteria_names]
    }


@pytest.fixture 
def alternatives(alternatives_names):
    return [{"id": name} for name in alternatives_names]


@pytest.fixture 
def criteria_scores():
    return [4, 7, 5, 8, 6, 6, 2, 5, 3, 7, 6, 6, 1/3, 1/3, 5, 3, 3, 1/5, 6, 3, 4, 0.5, 1/3, 1/4, 1/7, 1/2, 1/5, 1/5]


@pytest.fixture 
def alternatives_scores():
    return [1/7, 1/5, 3, 5, 9, 4, 4, 1/5, 1/9, 9, 4, 1/4, 1, 1, 1, 6, 4, 1/3, 9, 6, 1/3, 0.5, 0.5, 1]


@pytest.fixture 
def criteria_comparisons(criteria_names, criteria_scores):
    return list(map(merge_tuples, zip(combinations(criteria_names, 2), criteria_scores)))


@pytest.fixture 
def alternatives_comparisons(criteria_names, alternatives_names, alternatives_scores):
    comp = dict()
    for i, crit in enumerate(criteria_names):
        score = alternatives_scores[i*3: i*3 + 3]
        comp[crit] = list(map(merge_tuples, zip(combinations(alternatives_names, 2), score)))
    return comp


@pytest.fixture 
def data(criteria, alternatives, criteria_comparisons, alternatives_comparisons):
    return {
        "criteria": criteria,
        "alternatives": alternatives,
        "criteria_comparisons": criteria_comparisons,
        "alternatives_comparisons": alternatives_comparisons
    }




def test_foo(client, data):
    response = client.get('/ahp/pairwise', json=data)
    assert False, response.data