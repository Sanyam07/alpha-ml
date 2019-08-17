from copy import deepcopy
import hashlib
import os


def save_ease(*dargs, **dkargs):
    # get model dir.
    # deal with the parameters in decorators.
    if 'save_dir' not in dkargs:
        save_dir = './data/save_models'
    else:
        save_dir = dkargs['save_dir']
    if not save_dir.endswith('/'):
        save_dir += '/'
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)

    # if 'estimator_name' not in dkargs:
    #     name = 'default_model'
    # else:
    #     name = dkargs['estimator_name']

    # func : Evaluator.__call__(self,config)
    def _dec(func):
        def dec(*args, **kwargs):
            config = args[1]
            config = deepcopy(config)
            config_id = get_configuration_id(config)
            save_path = save_dir + "%s.pkl" % config_id
            # deal with the parameters in the function decorated.
            kwargs['save_path'] = save_path
            result = func(*args, **kwargs)
            return result

        return dec

    return _dec


def get_configuration_id(config):
    config_dict = config.get_dictionary()
    config_list = []
    for key, value in sorted(config_dict.items(), key=lambda t: t[0]):
        if isinstance(value, float):
            value = round(value, 5)
        config_list.append('%s-%s' % (key, str(value)))
    config_id = '_'.join(config_list)
    sha = hashlib.sha1(config_id.encode('utf8'))
    return sha.hexdigest()
