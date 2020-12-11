import argparse
import os
import sys
import json
import inquirer


__PYX_CONFIG__ = {
    'api_url': 'https://beta.pyx.ai/api/',
    'frameworks': ['pytorch', 'onnx'],
    'required_fields': ['name', 'paper_url', 'dataset', 'license', 'description_short', 'description_full'],
    # 'api_url': 'http://127.0.0.1:8888/api/'
}


__PYX_PROJECT_TEMPLATE__ = {
    'author': '',
    'project_name': '',
    'category_id': '',
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


def ensure_have_permissions(func):
    def wrapper_fn(*args, **kwargs):
        pyx_project = kwargs['pyx_project']

        if 'id' not in pyx_project:
            print('Can not find the id. If you have an approval please specify the model id:')
            print('$ pyx config --id <MODEL_ID>')
            return False

        # TODO: send request to pyx api

        func_output = func(*args, **kwargs)

        return func_output
    return wrapper_fn


def _sync_meta():
    if 'categories' in __PYX_CONFIG__:
        # TODO: invalidate sometime
        return

    import requests
    from urllib.parse import urljoin

    r = requests.get(urljoin(__PYX_CONFIG__["api_url"], 'categories'))
    categories_json = r.json()['categories']

    __PYX_CONFIG__['categories'] = categories_json
    _save_config()


def _get_template_path(subcategory_id):
    subcategory_obj = next(obj for obj in __PYX_CONFIG__['categories'] if obj['id'] == subcategory_id)
    category_obj = next(obj for obj in __PYX_CONFIG__['categories'] if obj['id'] == subcategory_obj['parent_id'])

    return '{}/{}'.format(category_obj['url'], subcategory_obj['url'])


def _get_category_choices(answers):
    root_id = None
    if 'category' in answers:
        root_id = answers['category']
    return [(i['name'], i['id']) for i in __PYX_CONFIG__['categories'] if i['parent_id'] == root_id]


def _load_config():
    """
    Load JSON config from ~/.pyx/pyx.json
    """
    import json

    config_path_dir = os.path.join(os.path.expanduser('~'), '.pyx')
    config_path = os.path.join(config_path_dir, 'pyx.json')

    if os.path.exists(config_path):
        global __PYX_CONFIG__
        with open(config_path, 'r') as f:
            __PYX_CONFIG__ = {**__PYX_CONFIG__, **json.load(f)}
            f.close()


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


def _add_framework(project_path_prefix, subcategory_id, framework, **kwargs):
    """
    Add model to the project
    """
    import os
    import pyx

    subcategory_path = _get_template_path(subcategory_id)

    pyx_boilerplate_path = os.path.join(
        os.path.dirname(pyx.__file__), 'boilerplates',
        subcategory_path,
        framework
    )

    if not os.path.exists(pyx_boilerplate_path):
        pyx_boilerplate_path = os.path.join(
            os.path.dirname(pyx.__file__), 'boilerplates', 'general',
            framework
        )

    if os.path.exists(pyx_boilerplate_path):
        print('Adding model ...')
        try:
            from shutil import copytree
            copytree(pyx_boilerplate_path, os.path.join(project_path_prefix, 'models', framework))
            print('...')
            print('Your boilerplate is ready to use. Please, run:')
            print('$ pyx run ' + framework)
            print('or :')
            print('$ cd models/{}'.format(framework))
            print('$ python PYX.py')
        except FileExistsError:
            print('Destination directory is already exist. Consider another name of the project.')
    else:
        print('Template for category {0} not found'.format(subcategory_path))


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


def create(args, unknown, **kwargs):
    """
    Create new project
    """

    project_name = None
    if len(unknown) == 1:
        project_name = unknown[0]

    questions = [
        inquirer.List('category',
                      message="What is the category of your project?",
                      choices=_get_category_choices,
                      ),
        inquirer.List('subcategory',
                      message="What is the subcategory of your project?",
                      choices=_get_category_choices,
                      ),
        inquirer.Text('project_name',
                      message="Please, specify project name",
                      default=project_name,
                      ),
        inquirer.Checkbox('frameworks',
                          message="Prepare boilerplates for specific frameworks",
                          choices=__PYX_CONFIG__['frameworks']
                          ),
    ]
    answers = inquirer.prompt(questions)

    project_name = answers['project_name']
    category_id = answers['subcategory']
    frameworks = answers['frameworks']

    import os
    import json
    try:
        print('Creating project ...')
        os.makedirs(project_name)
        os.makedirs(os.path.join(project_name, 'web'))
        os.makedirs(os.path.join(project_name, 'models'))
        os.makedirs(os.path.join(project_name, 'testing-data'))

        with open(os.path.join(project_name, 'pyx.json'), 'w') as f:
            pyx_project = {**__PYX_PROJECT_TEMPLATE__, 'project_name': project_name, 'category_id': category_id}
            f.write(json.dumps(pyx_project, indent=4))
            f.close()

            print('...')
            print('Your project is ready to use. Please go to the project folder:')
            print('$ cd ' + project_name)

            print('Your can also add boilerplates for your project:')
            print('$ pyx add {framework}')

            print('Please, place testing samples to:')
            print('{}/testing-data'.format(project_name))

            print('If you want to attach any images / gifs, place them to:')
            print('{}/web'.format(project_name))

            for framework in frameworks:
                _add_framework(project_name, category_id, framework)

    except FileExistsError:
        print('Destination directory is already exist. Consider another name of the project.')


@ensure_pyx_project
def configure(args, pyx_project, extra_fields, **kwargs):
    """
    Configure project
    """
    extra_fields = vars(extra_fields)
    for k in extra_fields:
        if k in pyx_project.keys():
            pyx_project[k] = extra_fields[k]

    for k in __PYX_CONFIG__['required_fields']:
        if k not in pyx_project:
            pyx_project[k] = ''

    questions = [
        inquirer.Text('name',
                      message="Please, specify model name", default=pyx_project['name']),
        inquirer.Text('paper_url',
                      message="Please, specify paper url if you have one", default=pyx_project['paper_url']),
        inquirer.Text('dataset',
                      message="Please, specify paper dataset you used", default=pyx_project['dataset']),
        inquirer.Text('license',
                      message="Please, specify license", default=pyx_project['license']),
        inquirer.Editor('description_short', message="Please, specify short description of your model",
                        default=pyx_project['description_short']),
        inquirer.Editor('description_full', message="Please, specify short detailed of your model",
                        default=pyx_project['description_full']),
    ]
    answers = inquirer.prompt(questions)
    for k in answers:
        pyx_project[k] = answers[k]

    print(json.dumps(pyx_project, indent=4))


@ensure_pyx_project
def add(args, pyx_project, **kwargs):
    """
    Add model to the project
    """
    print(args, kwargs)
    _add_framework('./', pyx_project['category_id'], args.framework)


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
            import tempfile
            sys.path.append('./models/' + model)
            from PYX import get_weight_paths, predict

            print('Testing model {} ...'.format(model))
            print('Initializing model ...')
            weight_paths = {i: os.path.join('./models/' + model, k) for i, k in get_weight_paths().items()}
            print(weight_paths)

            time_measures = []
            for i in range(10):
                with tempfile.TemporaryDirectory() as tmpdirname:
                    start = time.time()
                    predict('./testing-data', tmpdirname, weight_paths, 'cuda')
                    end = time.time()
                    time_measures.append(end - start)
                    print('Inference time: ', end - start)

            print('Mean inference time:', np.mean(time_measures))

            pyx_project['models'][model] = {
                'weight_paths': get_weight_paths(),
                'mean_inference_time': np.mean(time_measures),
            }

            print('....')
            print('PASSED')

            del get_weight_paths, predict
            del sys.modules["PYX"]

            from gc import collect
            collect()

            sys.path.pop()
        except Exception as e:
            print(e.with_traceback())
            print('....')
            print('An error occured.')
            return False

    return True


@ensure_pyx_project
def run_locally(args, pyx_project, extra_fields, **kwargs):
    import os
    import time
    import sys

    framework = args.framework
    input_dir = args.input_dir
    output_dir = args.output_dir

    os.makedirs(output_dir, exist_ok=True)

    try:
        sys.path.append('./models/' + framework)
        from PYX import get_weight_paths, predict

        print('Testing model {} ...'.format(framework))
        print('Initializing model ...')
        weight_paths = {i: os.path.join('./models/' + framework, k) for i, k in get_weight_paths().items()}
        print(weight_paths)

        start = time.time()
        completed = predict(input_dir, output_dir, weight_paths, 'cuda')
        if not completed:
            raise AssertionError

        end = time.time()
        print('Inference time: ', end - start)

        print('....')
        print('PASSED')

        del get_weight_paths, predict
        del sys.modules["PYX"]

        from gc import collect
        collect()

        sys.path.pop()
    except Exception as e:
        print(e.with_traceback())
        print('....')
        print('An error occured.')
        return False


@ensure_pyx_project
def publish(args, pyx_project, **kwargs):
    import requests
    from urllib.parse import urljoin

    for k in __PYX_CONFIG__['required_fields']:
        if k not in pyx_project:
            print('Required fields is missing. Consider configuring your project:')
            print('$ pyx configure')
            return

    from glob import glob
    pyx_project['web'] = [os.path.relpath(i, './web') for i in glob('./web/**', recursive=True) if os.path.isfile(i)]

    if 'id' in pyx_project:
        print('Updating project:')
        headers = {'Content-type': 'application/json', 'user-token': __PYX_CONFIG__["user_token"]}
        r = requests.put(urljoin(__PYX_CONFIG__["api_url"], 'models/' + str(pyx_project['id'])), headers=headers, json=pyx_project)
    else:
        headers = {'Content-type': 'application/json', 'user-token': __PYX_CONFIG__["user_token"]}
        r = requests.post(urljoin(__PYX_CONFIG__["api_url"], 'models'), headers=headers, json=pyx_project)

    try:
        print(r.status_code)
        print(r.json())
        for k in r.json():
            pyx_project[k] = r.json()[k]
    except:
        pass


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
        model_id = str(pyx_project['id'])
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

    version = 'latest'
    model_id = args.model_id
    if model_id.find(':') != -1:
        model_id, version = model_id.split(':')

    print('Downloading data ...')

    headers = {'user-token':  __PYX_CONFIG__["user_token"]}
    r = requests.get(urljoin(__PYX_CONFIG__["api_url"], 'models/' + model_id + '/download/' + version),
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


def cloud_run(args, extra_fields, **kwargs):
    # TODO: pack input_dir, send request, unpack to output_dir
    pass


def quotas(args, extra_fields, **kwargs):
    import requests
    from urllib.parse import urljoin

    headers = {'user-token': __PYX_CONFIG__["user_token"]}
    r = requests.get(urljoin(__PYX_CONFIG__["api_url"], 'quotas/'), headers=headers)

    if r.status_code == 200:
        print('Requests left: ', r.json()['requests'])
    else:
        print('An error occured. User is not registered or auth-token is broken. Try "pyx auth <token> first.')
        return


def users_remote_models(args, extra_fields, **kwargs):
    import requests
    from urllib.parse import urljoin

    headers = {'user-token': __PYX_CONFIG__["user_token"]}
    r = requests.get(urljoin(__PYX_CONFIG__["api_url"], 'users/'), headers=headers)

    if r.status_code == 200:
        if len(r.json()['orders']) > 0:
            print('My orders:')
            for i in r.json()['orders']:
                print('* (id: {id}) {license} {name}'.format(**i))
        if len(r.json()['models']) > 0:
            print('My models:')
            for i in r.json()['models']:
                print('* (id: {id}) {license} {name} (approved: {approved}) (published: {published})'.format(**i))
    else:
        print('An error occured. User is not registered or auth-token is broken. Try "pyx auth <token> first.')
        return


def main():
    _load_config()
    _sync_meta()

    parser = argparse.ArgumentParser(prog='pyx')

    subparsers = parser.add_subparsers(dest='mode', help='sub-command help')

    parser_auth = subparsers.add_parser('auth', help='Auth PYX user')
    parser_auth.add_argument('user_token', type=str, help='set user token')

    parser_create = subparsers.add_parser('create', help='Create a new PYX project (using wizard)')
    parser_configure = subparsers.add_parser('configure', help='Create a config file for a PYX project')

    parser_create = subparsers.add_parser('add', help='Add a model to a project')
    parser_create.add_argument('framework', type=str, help='the framework you want to add')

    parser_download = subparsers.add_parser('download', help='Pull a published workspace')
    parser_download.add_argument('model_id', type=str, help='model id from pyx.ai')
    parser_download.add_argument('project_name', type=str, help='destination project name')

    parser_publish = subparsers.add_parser('publish', help='Publish a project to pyx.ai')
    parser_upload = subparsers.add_parser('upload', help='Upload current workspace to pyx.ai')

    parser_cloud_run = subparsers.add_parser('cloud-run', help='Run model using pyx.ai cloud')
    parser_cloud_run.add_argument('model_name', type=str, help='a model path from pyx.ai (model-id/framework:version)')
    parser_cloud_run.add_argument('input_dir', type=str, help='directory with input samples')
    parser_cloud_run.add_argument('output_dir', type=str, help='directory with results')

    parser_run = subparsers.add_parser('run', help='Perform inference locally')
    parser_run.add_argument('framework', type=str, help='framework to perform inference on')
    parser_run.add_argument('input_dir', type=str, help='directory with input samples')
    parser_run.add_argument('output_dir', type=str, help='directory with results')

    _ = subparsers.add_parser('quotas', help='Check pyx-cloud quotas')
    _ = subparsers.add_parser('my-remote-models', help='List available models from PYX')

    _ = subparsers.add_parser('test', help='Run tests locally')

    # print help
    if len(sys.argv) < 2:
        parser.print_usage()
        sys.exit(1)

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
        'configure': configure,
        'add': add,
        'test': test,
        'publish': publish,
        'upload': upload,
        'download': download,
        'cloud-run': cloud_run,
        'run': run_locally,
        'quotas': quotas,
        'my-remote-models': users_remote_models,
    }

    subprogs[params.mode](params, extra_fields=extra_params, unknown=unknown)
    _save_config()
