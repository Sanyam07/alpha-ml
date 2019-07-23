import time
import logging
import numpy as np
from alphaml.engine.evaluator.base import BaseClassificationEvaluator, BaseRegressionEvaluator
from alphaml.utils.constants import MAX_INT


class BaseOptimizer(object):
    def __init__(self, evaluator, config_space, data, metric, seed):
        # Prepare the basics for evaluator.
        assert isinstance(evaluator, (BaseClassificationEvaluator, BaseRegressionEvaluator))
        self.evaluator = evaluator
        self.evaluator.data_manager = data
        self.evaluator.metric_func = metric
        self.config_space = config_space
        if seed is None:
            seed = np.random.random_integers(MAX_INT)
        self.seed = seed
        self.start_time = time.time()
        self.timing_list = list()
        self.incumbent = None
        self.logger = logging.getLogger(__name__)
        self.logger.info('The random seed is: %d' % self.seed)

    def run(self):
        raise NotImplementedError
