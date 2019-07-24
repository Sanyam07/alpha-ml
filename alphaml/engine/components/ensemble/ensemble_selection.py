from alphaml.engine.components.ensemble.base_ensemble import *
from alphaml.engine.components.data_manager import DataManager
from alphaml.utils.common import get_max_index
import numpy as np
from collections import Counter


class EnsembleSelection(BaseEnsembleModel):
    def __init__(self, model_info, ensemble_size, task_type, metric, model_type='ml', mode='fast',
                 sorted_initialization=False, n_best=15):
        super().__init__(model_info, ensemble_size, task_type, model_type)
        self.sorted_initialization = sorted_initialization
        self.config_list = self.model_info[0]
        if n_best < self.ensemble_size:
            self.n_best = n_best
        else:
            self.n_best = self.ensemble_size
        self.metric = metric
        self.mode = mode
        self.random_state = np.random.RandomState(42)

    def fit(self, dm: DataManager):
        # Train the basic models on this training set.
        if self.model_type == 'ml':
            predictions = []
            for config in self.config_list:
                estimator = self.get_estimator(config)
                estimator.fit(dm.train_X, dm.train_y)
                self.ensemble_models.append(estimator)
                pred = self.get_predictions(estimator, dm.val_X)
                predictions.append(pred)
                self._fit(predictions, dm.val_y)

        elif self.model_type == 'dl':
            pass

        return self

    def _fit(self, predictions, labels):
        self.ensemble_size = int(self.ensemble_size)
        if self.ensemble_size < 1:
            raise ValueError('Ensemble size cannot be less than one!')
        if self.mode not in ('fast', 'slow'):
            raise ValueError('Unknown mode %s' % self.mode)
        if self.mode == 'fast':
            self._fast(predictions, labels)
        else:
            self._slow(predictions, labels)
        self._calculate_weights()
        return self

    def _fast(self, predictions, labels):
        """Fast version of Rich Caruana's ensemble selection method."""
        self.num_input_models_ = len(predictions)

        ensemble = []
        trajectory = []
        order = []

        ensemble_size = self.ensemble_size

        if self.sorted_initialization:
            indices = self._sorted_initialization(predictions, labels, self.n_best)
            for idx in indices:
                ensemble.append(predictions[idx])
                order.append(idx)
                ensemble_ = np.array(ensemble).mean(axis=0)
                ensemble_performance = self.calculate_score(
                    pred=ensemble_,
                    y_true=labels)
                trajectory.append(ensemble_performance)
            ensemble_size -= self.n_best

        for i in range(ensemble_size):
            scores = np.zeros((len(predictions)))
            s = len(ensemble)
            if s == 0:
                weighted_ensemble_prediction = np.zeros(predictions[0].shape)
            else:
                # Memory-efficient averaging!
                ensemble_prediction = np.zeros(ensemble[0].shape)
                for pred in ensemble:
                    ensemble_prediction += pred
                ensemble_prediction /= s

                weighted_ensemble_prediction = (s / float(s + 1)) * \
                                               ensemble_prediction
            fast_ensemble_prediction = np.zeros(weighted_ensemble_prediction.shape)
            for j, pred in enumerate(predictions):
                fast_ensemble_prediction[:, :] = weighted_ensemble_prediction + \
                                                 (1. / float(s + 1)) * pred
                scores[j] = 1 - self.calculate_score(
                    pred=fast_ensemble_prediction,
                    y_true=labels)

            all_best = np.argwhere(scores == np.nanmin(scores)).flatten()
            best = self.random_state.choice(all_best)
            ensemble.append(predictions[best])
            trajectory.append(scores[best])
            order.append(best)

            # Handle special case
            if len(predictions) == 1:
                break

        self.indices_ = order
        self.trajectory_ = trajectory
        self.train_score_ = trajectory[-1]

    def _slow(self, predictions, labels):
        """Rich Caruana's ensemble selection method."""
        self.num_input_models_ = len(predictions)

        ensemble = []
        trajectory = []
        order = []

        ensemble_size = self.ensemble_size

        if self.sorted_initialization:
            indices = self._sorted_initialization(predictions, labels, self.n_best)
            for idx in indices:
                ensemble.append(predictions[idx])
                order.append(idx)
                ensemble_ = np.array(ensemble).mean(axis=0)
                ensemble_performance = self.calculate_score(
                    pred=ensemble_,
                    y_true=labels)
                trajectory.append(ensemble_performance)
            ensemble_size -= self.n_best

        for i in range(ensemble_size):
            scores = np.zeros([len(predictions)])
            for j, pred in enumerate(predictions):
                ensemble.append(pred)
                ensemble_prediction = np.mean(np.array(ensemble), axis=0)
                scores[j] = 1 - self.calculate_score(
                    pred=ensemble_prediction,
                    y_true=labels)
                ensemble.pop()
            best = np.nanargmin(scores)
            ensemble.append(predictions[best])
            trajectory.append(scores[best])
            order.append(best)

            # Handle special case
            if len(predictions) == 1:
                break

        self.indices_ = np.array(order)
        self.trajectory_ = np.array(trajectory)
        self.train_score_ = trajectory[-1]

    def _sorted_initialization(self, predictions, labels, n_best):
        perf = np.zeros([predictions.shape[0]])

        for idx, prediction in enumerate(predictions):
            perf[idx] = self.calculate_score(pred=prediction, y_true=labels)

        indices = np.argsort(perf)[perf.shape[0] - n_best:]
        return indices

    def _calculate_weights(self):
        ensemble_members = Counter(self.indices_).most_common()
        weights = np.zeros((self.num_input_models_,), dtype=float)
        for ensemble_member in ensemble_members:
            weight = float(ensemble_member[1]) / self.ensemble_size
            weights[ensemble_member[0]] = weight

        if np.sum(weights) < 1:
            weights = weights / np.sum(weights)

        self.weights_ = weights

    def predict(self, X):
        predictions = []
        for estimator in self.ensemble_models:
            pred = self.get_predictions(estimator, X)
            predictions.append(pred)
        predictions = np.asarray(predictions)

        # if predictions.shape[0] == len(self.weights_),
        # predictions include those of zero-weight models.
        if predictions.shape[0] == len(self.weights_):
            pred = np.average(predictions, axis=0, weights=self.weights_)

        # if prediction model.shape[0] == len(non_null_weights),
        # predictions do not include those of zero-weight models.
        elif predictions.shape[0] == np.count_nonzero(self.weights_):
            non_null_weights = [w for w in self.weights_ if w > 0]
            pred = np.average(predictions, axis=0, weights=non_null_weights)

        # If none of the above applies, then something must have gone wrong.
        else:
            raise ValueError("The dimensions of ensemble predictions"
                             " and ensemble weights do not match!")
        if self.task_type == CLASSIFICATION:
            return np.argmax(pred, axis=-1)
        elif self.task_type == REGRESSION:
            return pred

    def calculate_score(self, pred, y_true):
        if self.task_type == CLASSIFICATION:
            if len(pred) == 1 or pred.shape[1] == 1:
                pred = [int(i > 0.5) for i in pred]
            else:
                pred = np.argmax(pred, axis=1)
            score = self.metric(pred, y_true)
        elif self.task_type == REGRESSION:
            score = -self.metric(pred, y_true)
        # We want to maximize score
        return score