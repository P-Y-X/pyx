import os
import json
from datetime import datetime
import requests
from urllib.parse import urljoin


__PYX_CONFIG__ = {
    'api_url': 'https://beta.pyx.ai/api/',
    'frameworks': ['pytorch', 'onnx', 'tensorflow', 'gluon'],
    'required_fields': ['name', 'paper_url', 'dataset', 'license', 'description_short', 'description_full', 'price'],
    'last_meta_update': 0.0,
    # 'api_url': 'http://127.0.0.1:8888/api/'
}


__PYX_PROJECT_TEMPLATE__ = {
    'author': '',
    'project_name': '',
    'category_id': '',
}

__PYX_MODULE_TEMPLATE__ = {
    'framework': '',
    'model_id': '',
}


def ensure_pyx_project(func):
    def wrapper_fn(*args, **kwargs):
        if not os.path.exists('pyx.json'):
            print('Cant find pyx.json. Are you in a pyx-project directory?')
            return False

        with open(os.path.join('pyx.json'), 'r') as f:
            pyx_project_json = json.load(f)
            f.close()

        func_output = func(*args, **{**kwargs, 'pyx_project': pyx_project_json})

        with open(os.path.join('pyx.json'), 'w') as f:
            f.write(json.dumps(pyx_project_json, indent=4))
            f.close()

        return func_output
    return wrapper_fn


def ensure_pyx_module(func):
    def wrapper_fn(*args, **kwargs):
        if not os.path.exists('pyx_module.json'):
            print('Cant find pyx_module.json. Do you have pyx_module.json in your directory?')
            return False

        with open(os.path.join('pyx_module.json'), 'r') as f:
            pyx_module_json = json.load(f)
            f.close()

        func_output = func(*args, **{**kwargs, 'pyx_module': pyx_module_json})

        with open(os.path.join('pyx_module.json'), 'w') as f:
            f.write(json.dumps(pyx_module_json, indent=4))
            f.close()

        return func_output
    return wrapper_fn


def ensure_have_permissions(func):
    def wrapper_fn(*args, **kwargs):
        pyx_project = kwargs['pyx_project']

        if 'id' not in pyx_project:
            print('Can not find the id. May be you need to run first:')
            print('$ pyx publish')
            return False

        # TODO: send request to pyx api

        func_output = func(*args, **kwargs)

        return func_output
    return wrapper_fn


def with_pyx_config(func):
    def wrapper_fn(*args, **kwargs):
        pyx_config = _load_config()
        _sync_meta(pyx_config)

        func_output = func(*args, **{**kwargs, 'pyx_config': pyx_config})

        _save_config(pyx_config)

        return func_output
    return wrapper_fn


def _sync_meta(pyx_config):
    if 'categories' in pyx_config:
        if 'last_meta_update' in pyx_config:
            if datetime.timestamp(datetime.now()) - pyx_config['last_meta_update'] < 60 * 60:
                # Cache for 1 hour
                return

    print('Updating meta information...')
    r = requests.get(urljoin(pyx_config["api_url"], 'categories'))
    if r.status_code == 200:
        categories_json = r.json()['categories']
        pyx_config['last_meta_update'] = datetime.timestamp(datetime.now())
        pyx_config['categories'] = categories_json
        _save_config(pyx_config)
    else:
        print('An error occurred. Please, check your connection and try again later.')


@with_pyx_config
def _get_template_path(subcategory_id, pyx_config):
    subcategory_obj = next(obj for obj in pyx_config['categories'] if obj['id'] == subcategory_id)
    category_obj = next(obj for obj in pyx_config['categories'] if obj['id'] == subcategory_obj['parent_id'])

    return '{}/{}'.format(category_obj['url'], subcategory_obj['url'])


@with_pyx_config
def _get_category_choices(answers, pyx_config):
    root_id = None
    if 'category' in answers:
        root_id = answers['category']
    return [(i['name'], i['id']) for i in pyx_config['categories'] if i['parent_id'] == root_id]


def _load_config():
    """
    Load JSON config from ~/.pyx/pyx.json
    """
    import json

    config_path_dir = os.path.join(os.path.expanduser('~'), '.pyx')
    config_path = os.path.join(config_path_dir, 'pyx.json')

    pyx_config = __PYX_CONFIG__
    if os.path.exists(config_path):
        with open(config_path, 'r') as f:
            pyx_config = {**pyx_config, **json.load(f)}
            f.close()

    return pyx_config


def _save_config(pyx_config):
    """
    Save JSON config to ~/.pyx/pyx.json
    """
    import os
    import json

    config_path_dir = os.path.join(os.path.expanduser('~'), '.pyx')
    config_path = os.path.join(config_path_dir, 'pyx.json')

    os.makedirs(config_path_dir, exist_ok=True)
    with open(config_path, 'w') as f:
        f.write(json.dumps(pyx_config, indent=4))
        f.close()
