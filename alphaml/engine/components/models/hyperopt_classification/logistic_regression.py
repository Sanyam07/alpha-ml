import numpy as np
from hyperopt import hp
from alphaml.utils.constants import *
from alphaml.engine.components.models.base_model import BaseClassificationModel


class Logistic_Regression(BaseClassificationModel):
    def __init__(self, C, penalty, solver, tol, max_iter, random_state=None):
        self.C = C
        self.tol = tol
        self.random_state = random_state
        self.penalty = penalty
        self.solver = solver
        self.max_iter = max_iter
        self.estimator = None

    def fit(self, X, Y):
        from sklearn.linear_model import LogisticRegression

        self.C = float(self.C)

        self.estimator = LogisticRegression(random_state=self.random_state,
                                            solver=self.solver,
                                            penalty=self.penalty,
                                            multi_class='ovr',
                                            C=self.C,
                                            tol=self.tol,
                                            max_iter=self.max_iter,
                                            n_jobs=-1)
        self.estimator.fit(X, Y)
        return self

    def predict(self, X):
        if self.estimator is None:
            raise NotImplementedError
        return self.estimator.predict(X)

    def predict_proba(self, X):
        if self.estimator is None:
            raise NotImplementedError()
        return self.estimator.predict_proba(X)

    @staticmethod
    def get_properties(dataset_properties=None):
        return {'shortname': 'Logistic-Regression',
                'name': 'Logistic Regression Classification',
                'handles_regression': False,
                'handles_classification': True,
                'handles_multiclass': True,
                'handles_multilabel': False,
                'is_deterministic': True,
                'input': (DENSE, SPARSE, UNSIGNED_DATA),
                'output': (PREDICTIONS,)}

    @staticmethod
    def get_hyperparameter_search_space(dataset_properties=None):
        space = {'C': hp.loguniform('lr_C', np.log(0.03125), np.log(10)),
                 'tol': hp.loguniform('lr_tol', np.log(1e-6), np.log(1e-2)),
                 'max_iter': hp.uniform('lr_max_iter', 100, 1000),
                 'penalty': hp.choice('lr_penalty', ["l1", "l2"]),
                 'solver': hp.choice('lr_solver', ["liblinear", "saga"])}

        init_trial = {'C': 1, 'tol': 1e-4, 'max_iter': 100, 'penalty': "l2", 'solver': "liblinear"}

        return space
