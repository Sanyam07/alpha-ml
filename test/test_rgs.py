import warnings
from sklearn.preprocessing import LabelEncoder
import sys
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--run_count', type=int, default=300)
parser.add_argument('--ensemble_size', type=int, default=12)
args = parser.parse_args()

warnings.filterwarnings("ignore")
sys.path.append("/home/daim_gpu/sy/AlphaML")

'''
Available models:
adaboost, decision_tree, extra_trees, gaussian_nb, gradient_boosting, k_nearest_neighbors, lda, liblinear_svc,
libsvm_svc, logistic_regression, mlp, passive_aggressive, qda, random_forest, sgd, xgboost
'''


def test_cash_module():
    from alphaml.engine.components.data_manager import DataManager
    from alphaml.estimators.regressor import Regressor
    from alphaml.datasets.rgs_dataset.dataset_loader import load_data
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import mean_squared_error
    import random
    result = []
    for i in range(1):
        x, y, _ = load_data('boston')

        dm = DataManager(x, y, val_size=0.33, random_state=random.randint(1, 255), stratify=False)
        cls = Regressor(
            optimizer='baseline',
            ensemble_method='bagging',
            ensemble_size=args.ensemble_size,
        ).fit(dm, metric='mse', update_mode=2, runcount=args.run_count)

        pred = cls.predict(dm.val_X)
        print(pred)
        result.append(mean_squared_error(dm.val_y, pred))
        print(result)


if __name__ == "__main__":
    test_cash_module()
