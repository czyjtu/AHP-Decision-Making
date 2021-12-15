from src import create_app
from src.decision_making.ahp.comparison_matrix import ComprehensionMatrix
from src.decision_making.base import Preference

if __name__ == '__main__':
    create_app().run(debug=True, port=8800)
