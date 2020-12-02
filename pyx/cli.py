import argparse
import os
import json


__PYX_CONFIG__ = {
    'api_url': 'https://beta.pyx.ai/api/'
    # 'api_url': 'http://127.0.0.1:8888/api/'
}


__PYX_PROJECT_TEMPLATE__ = {
    'project_name': '',
    'model_id': '',
    'category_id': '',
    'category': '',
    'author': '',
    'license': '',
}


def list_available_categories():
    import pyx
    root_categories = os.listdir(os.path.join(os.path.dirname(pyx.__file__), 'boilerplates'))
    for root_category in root_categories:
        print(root_category)
        nested_categories = os.listdir(os.path.join(os.path.dirname(pyx.__file__), 'boilerplates', root_category))
        for nested_category in nested_categories:
            print('-- {} ({}/{})'.format(nested_category, root_category, nested_category))


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


def ensure_have_permissions(func):
    def wrapper_fn(*args, **kwargs):
        pyx_project = kwargs['pyx_project']

        if 'model_id' not in pyx_project or len(pyx_project['model_id']) == 0:
            print('Cant find model-id. if you have got an approval, please specify model id:')
            print('$ pyx config --model-id <MODEL_ID>')
            return False

        # if 'category_id' not in pyx_project or len(pyx_project['category_id']) == 0:
        #     print('Cant find category-id. if you have got an approval, please specify category id:')
        #     print('$ pyx config --category-id <CATEGORY_ID>')
        #     return False

        # TODO: send request to pyx api

        func_output = func(*args, **kwargs)

        return func_output
    return wrapper_fn


def _load_config():
    """
    Load JSON config from ~/.pyx/pyx.json
    """
    import json

    config_path_dir = os.path.join(os.path.expanduser('~'), '.pyx')
    config_path = os.path.join(config_path_dir, 'pyx.json')

    if os.path.exists(config_path):
        global __PYX_CONFIG__
        __PYX_CONFIG__ = {**__PYX_CONFIG__, **json.load(open(config_path, 'r'))}


def _save_config():
    """
    Save JSON config to ~/.pyx/pyx.json
    """
    import os
    import json

    config_path_dir = os.path.join(os.path.expanduser('~'), '.pyx')
    config_path = os.path.join(config_path_dir, 'pyx.json')

    os.makedirs(config_path_dir, exist_ok=True)
    with open(config_path, 'w') as f:
        f.write(json.dumps(__PYX_CONFIG__, indent=4))
        f.close()


def auth(args, **kwargs):
    """
    Authorization
    """
    __PYX_CONFIG__['user_token'] = args.user_token

    # TODO: check user creds
    import requests
    from urllib.parse import urljoin
    headers = {'user-token': __PYX_CONFIG__["user_token"]}

    r = requests.get(
        urljoin(__PYX_CONFIG__["api_url"], 'auth/check'),
        params={},
        headers=headers
    )

    if r.status_code == 200:
        print('Authorized.')
        _save_config()
    else:
        print('Wrong token.')


def list_templates(args, **kwargs):
    """
    List available templates
    """
    list_available_categories()


def create(args, **kwargs):
    """
    Create new project
    """
    import os
    import json
    try:
        print('Creating project ...')
        os.makedirs(args.project_name)
        os.makedirs(os.path.join(args.project_name, 'web'))
        os.makedirs(os.path.join(args.project_name, 'models'))
        with open(os.path.join(args.project_name, 'pyx.json'), 'w') as f:
            pyx_project = {**__PYX_PROJECT_TEMPLATE__, 'project_name': args.project_name, 'category': args.category}
            f.write(json.dumps(pyx_project, indent=4))
            f.close()

            print('...')
            print('Your project is ready to use. Please go to the project folder:')
            print('$ cd ' + args.project_name)

            print('Your can also add boilerplates for your project:')
            print('$ pyx add {framework}')

    except FileExistsError:
        print('Destination directory is already exist. Consider another name of the project.')


@ensure_pyx_project
def config(args, pyx_project, extra_fields, **kwargs):
    """
    Configure project
    """
    extra_fields = vars(extra_fields)
    for k in extra_fields:
        if k in pyx_project.keys():
            pyx_project[k] = extra_fields[k]

    print(json.dumps(pyx_project, indent=4))


@ensure_pyx_project
def add(args, pyx_project, **kwargs):
    """
    Add model to the project
    """
    import os
    import pyx

    pyx_boilerplate_path = os.path.join(
        os.path.dirname(pyx.__file__), 'boilerplates',
        pyx_project['category'],
        args.framework
    )

    if not os.path.exists(pyx_boilerplate_path):
        pyx_boilerplate_path = os.path.join(
            os.path.dirname(pyx.__file__), 'boilerplates', 'general',
            args.framework
        )

    if os.path.exists(pyx_boilerplate_path):
        print('Adding model ...')
        try:
            from shutil import copytree
            copytree(pyx_boilerplate_path, os.path.join('models', args.framework))
            print('...')
            print('Your boilerplate is ready to use. Please, run:')
            print('$ pyx run ' + args.framework)
            print('or :')
            print('$ cd models/{}'.format(args.framework))
            print('$ python PYX.py')
        except FileExistsError:
            print('Destination directory is already exist. Consider another name of the project.')
    else:
        print('Template for category {0} not found'.format(args.category))


@ensure_pyx_project
def test(*args, pyx_project, **kwargs):
    """
    Test model / models inside the project
    """
    import os
    import time
    import numpy as np

    print('Testing project ...')

    pyx_project['models'] = {}
    models = os.listdir('models')
    for model in models:
        try:
            import sys
            sys.path.append('./models/' + model)
            from PYX import PYXImplementedModel

            print('Testing model {} ...'.format(model))
            print('Initializing model ...')
            project = PYXImplementedModel()
            project.initialize()
            project.set_weights()

            print('inputs: ', project.get_input_shapes())
            print('inputs: ', project.get_input_types())
            print('....')

            time_measures = []
            for i in range(10):
                test_sample = {}
                inputs = project.get_input_shapes()

                for k in inputs:
                    test_sample[k] = np.zeros(inputs[k])

                start = time.time()
                _ = project.predict(test_sample)
                end = time.time()
                time_measures.append(end - start)
                print('Inference time: ', end - start)

            print('Mean inference time:', np.mean(time_measures))
            pyx_project['models'][model] = {
                'input_shapes': project.get_input_shapes(),
                'input_types': project.get_input_types(),
                'mean_inference_time': np.mean(time_measures),
            }

            print('....')
            print('PASSED')
            sys.path.pop()
        except:
            print('....')
            print('An error occured.')
            return False

        return True


@ensure_pyx_project
@ensure_have_permissions
def upload(args, pyx_project, **kwargs):
    import requests
    from urllib.parse import urljoin
    import shutil
    import os
    import tempfile

    with tempfile.TemporaryDirectory() as tmpdirname:
        print('Packing current project ...')
        shutil.make_archive(os.path.join(tmpdirname, '_project'), 'zip', '.')

        print('Uploading data ...')
        model_id = pyx_project['model_id']
        fileobj = open(os.path.join(tmpdirname, '_project.zip'), 'rb')
        headers = {'user-token':  __PYX_CONFIG__["user_token"]}
        r = requests.post(urljoin(__PYX_CONFIG__["api_url"], 'models/' + model_id + '/upload'),
                          headers=headers,
                          files={"project_files": ("project.zip", fileobj)})
        print(r.status_code)
        if r.status_code == 200:
            print('Succesfully uploaded.')
        else:
            print('An error occured.')


def download(args, **kwargs):
    import requests
    from urllib.parse import urljoin
    import shutil
    import os
    import tempfile

    print('Downloading data ...')

    headers = {'user-token':  __PYX_CONFIG__["user_token"]}
    r = requests.get(urljoin(__PYX_CONFIG__["api_url"], 'models/' + args.model_id + '/download'),
                     headers=headers, stream=True)

    if r.status_code == 200:
        print('Succesfully pulled ...')
    else:
        print('An error occured.')
        return

    with tempfile.TemporaryDirectory() as tmpdirname:
        print('Packing current project ...')
        with open(os.path.join(tmpdirname, 'src.zip'), 'wb') as out_file:
            shutil.copyfileobj(r.raw, out_file)

        shutil.unpack_archive(os.path.join(tmpdirname, 'src.zip'), args.project_name)

        print('....')
        print('DONE')


def predict(args, extra_fields):
    import requests
    from urllib.parse import urljoin

    model_id, framework = args.model_name.split('/')

    def base64_encode_file(file_to_encode):
        import base64
        return base64.b64encode(open(file_to_encode, 'rb').read())

    data = {}

    extra_fields = vars(extra_fields)
    for k in extra_fields:
        data[k] = base64_encode_file(extra_fields[k]).decode("utf-8")

    headers = {'user-token': __PYX_CONFIG__["user_token"]}
    r = requests.post(urljoin(__PYX_CONFIG__["api_url"], 'models/' + model_id + '/predict/' + framework),
                      headers=headers, json=data)
    print(r.status_code, r.content)
    if r.status_code == 200:
        print('Succesfully predicted ...', r.json())
    else:
        print('An error occured.')
        return


def quotas(args, extra_fields):
    import requests
    from urllib.parse import urljoin

    headers = {'user-token': __PYX_CONFIG__["user_token"]}
    r = requests.get(urljoin(__PYX_CONFIG__["api_url"], 'quotas/'), headers=headers)

    if r.status_code == 200:
        print('Requests left: ', r.json()['requests'])
    else:
        print('An error occured. User is not registered or auth-token is broken. Try "pyx auth <token> first.')
        return


def main():
    _load_config()
    print(__PYX_CONFIG__)
    parser = argparse.ArgumentParser(prog='pyx')

    subparsers = parser.add_subparsers(dest='mode', help='sub-command help')

    parser_auth = subparsers.add_parser('auth', help='Auth PYX user')
    parser_auth.add_argument('user_token', type=str, help='set user token')

    parser_list_templates = subparsers.add_parser('list-templates', help='List available templates')

    parser_create = subparsers.add_parser('create', help='Create new PYX project')
    parser_create.add_argument('project_name', type=str, help='a name of new project (e.g. resnet-test)')
    parser_create.add_argument('category', type=str, help='a category of a new project (e.g. cv/classification)')

    parser_config = subparsers.add_parser('config', help='Configure PYX project')

    parser_create = subparsers.add_parser('add', help='Add model to the project')
    parser_create.add_argument('framework', type=str, help='the framework you want to add')

    parser_download = subparsers.add_parser('download', help='Pull published workspace')
    parser_download.add_argument('model_id', type=str, help='model id from pyx.ai')
    parser_download.add_argument('project_name', type=str, help='destination project name')

    parser_upload = subparsers.add_parser('upload', help='Upload current workspace to pyx.ai')

    parser_predict = subparsers.add_parser('predict', help='Push current workspace to pyx.ai')
    parser_predict.add_argument('model_name', type=str, help='a magic url from pyx.ai (model-id/framework)')

    _ = subparsers.add_parser('quotas', help='Check pyx-cloud quotas')

    _ = subparsers.add_parser('test', help='Run tests locally')

    params, unknown = parser.parse_known_args()  # this is an 'internal' method
    # which returns 'parsed', the same as what parse_args() would return
    # and 'unknown', the remainder of that
    # the difference to parse_args() is that it does not exit when it finds redundant arguments

    extra_fields_parser = argparse.ArgumentParser()
    for arg in unknown:
        if arg.startswith(("-", "--")):
            # you can pass any arguments to add_argument
            extra_fields_parser.add_argument(arg, type=str)

    extra_params, _ = extra_fields_parser.parse_known_args()

    subprogs = {
        'auth': auth,
        'create': create,
        'config': config,
        'list-templates': list_templates,
        'add': add,
        'test': test,
        'upload': upload,
        'download': download,
        'predict': predict,
        'quotas': quotas,
    }

    subprogs[params.mode](params, extra_fields=extra_params)
