import argparse
import os
import sys
import json
import inquirer

from pyx_cli.misc import __PYX_PROJECT_TEMPLATE__, __PYX_CONFIG__
from pyx_cli.misc import _save_config, _get_category_choices, _get_template_path
from pyx_cli.misc import ensure_pyx_project, ensure_have_permissions, with_pyx_config


class UploadInChunks(object):
    def __init__(self, filename, chunksize=1 << 13):
        self.filename = filename
        self.chunksize = chunksize
        self.totalsize = os.path.getsize(filename)
        self.readsofar = 0

    def __iter__(self):
        with open(self.filename, 'rb') as file:
            while True:
                data = file.read(self.chunksize)
                if not data:
                    sys.stderr.write("\n")
                    break
                self.readsofar += len(data)
                percent = self.readsofar * 1e2 / self.totalsize
                sys.stderr.write("\r{percent:3.0f}%".format(percent=percent))
                yield data

    def __len__(self):
        return self.totalsize


def _add_framework(category_id, framework, **kwargs):
    """
    Add model to the project
    """
    import os
    import pyx

    subcategory_path = _get_template_path(category_id)

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
        print('Adding framework ...')

        if not os.path.exists('PYX.py'):
            from shutil import copyfile
            copyfile(os.path.join(pyx_boilerplate_path, 'pyx-endpoints.py'),
                     'pyx_endpoints.py')

        else:
            print('Destination PYX.py is already exists.')
    else:
        print('Template for category {0} not found'.format(subcategory_path))


@with_pyx_config
def auth(args, pyx_config, **kwargs):
    """
    Authorization
    """
    pyx_config['user_token'] = args.user_token

    import requests
    from urllib.parse import urljoin
    headers = {'user-token': pyx_config["user_token"]}

    r = requests.get(
        urljoin(__PYX_CONFIG__["api_url"], 'auth/check'),
        params={},
        headers=headers
    )

    if r.status_code == 200:
        print('Authorized.')
    else:
        pyx_config['user_token'] = ''
        print('Wrong token.')


def create(args, **kwargs):
    """
    Create new project
    """
    import os

    project_name = os.path.basename(os.getcwd())

    questions = [
        inquirer.List('category',
                      message="What is the category of your project?",
                      choices=_get_category_choices,
                      ),
        inquirer.List('subcategory',
                      message="What is the subcategory of your project?",
                      choices=_get_category_choices,
                      ),
        inquirer.List('framework',
                      message="Prepare boilerplate for specific framework",
                      choices=__PYX_CONFIG__['frameworks']
                      ),
    ]

    answers = inquirer.prompt(questions)

    category_id = answers['subcategory']
    framework = answers['framework']

    try:
        print('Creating project ...')
        os.makedirs('pyx-web')
        os.makedirs('pyx-testing-data')

        with open('pyx-web/description.md', 'w') as f:
            f.write('# {}\n'.format(project_name))
            f.close()

        with open('pyx.json', 'w') as f:
            pyx_project = {**__PYX_PROJECT_TEMPLATE__,
                           'category_id': category_id,
                           'framework': framework
                           }

            f.write(json.dumps(pyx_project, indent=4))
            f.close()

            print('...')
            print('Your project is ready to use.')

            print('Please, place testing samples to:')
            print('./pyx-testing-data')

            print('If you want to attach any images / gifs, place them to:')
            print('./pyx-web')

            _add_framework(category_id=category_id, framework=framework)

            print('Configuring project:')
            print('You can change these parameters after by running:')
            print('$ pyx configure')

            configure(pyx_project)

    except FileExistsError:
        print('Destination directory is already exist. Consider another name of the project.')


@ensure_pyx_project
def configure(args, pyx_project, **kwargs):
    """
    Configure project
    """

    questions = [
        inquirer.Text('name',
                      message="Please, specify model name", default=pyx_project['name']),
        inquirer.Text('paper_url',
                      message="Please, specify paper url if you have one", default=pyx_project['paper_url']),
        inquirer.Text('dataset',
                      message="Please, specify dataset you used", default=pyx_project['dataset']),
        inquirer.Text('license',
                      message="Please, specify license", default=pyx_project['license']),
        inquirer.Text('price',
                      message="Please, specify price (0.0 for free models)", default=pyx_project['price']),
        inquirer.Editor('description_short', message="Please, specify short description of your model",
                        default=pyx_project['description_short']),
    ]

    answers = inquirer.prompt(questions)
    for k in answers:
        pyx_project[k] = answers[k]

    print("pyx.json:")
    print(json.dumps(pyx_project, indent=4))


def attach(args, **kwargs):
    """
    Add pyx-module to a project
    """
    questions = [
        inquirer.List('category',
                      message="What is the category of your project?",
                      choices=_get_category_choices,
                      ),
        inquirer.List('subcategory',
                      message="What is the subcategory of your project?",
                      choices=_get_category_choices,
                      ),
        inquirer.Text('model_id',
                      message="Set existing model id",
                      default=None,
                      ),
        inquirer.List('framework',
                      message="Prepare boilerplate for specific framework",
                      choices=__PYX_CONFIG__['frameworks']
                      ),
    ]

    answers = inquirer.prompt(questions)

    category_id = answers['subcategory']
    framework = answers['framework']
    model_id = answers['model_id']

    with open('pyx.json', 'w') as f:
        f.write(json.dumps({
            'framework': framework,
            'id': model_id
        }, indent=4))

    _add_framework(category_id=category_id, model_id=model_id, framework=framework)


@ensure_pyx_project
def test(*args, pyx_project, **kwargs):
    """
    Test model / models inside the project
    """
    import os
    import time
    import numpy as np

    print('Testing project ...')

    pyx_project['meta'] = {}

    try:
        import sys
        import tempfile
        sys.path.append('.')
        from pyx_endpoints import get_weight_paths, predict

        print('Testing model ...')
        print('Initializing model ...')
        weight_paths = {i: k for i, k in get_weight_paths().items()}
        print('weight_paths: ', weight_paths)

        time_measures = []
        for i in range(10):
            with tempfile.TemporaryDirectory() as tmpdirname:
                start = time.time()
                predict('./pyx-testing-data', tmpdirname, weight_paths, 'cuda')
                end = time.time()
                time_measures.append(end - start)
                print('Inference time: ', end - start)

        print('Mean inference time:', np.mean(time_measures))

        pyx_project['meta'] = {
            'weight_paths': get_weight_paths(),
            'mean_inference_time': np.mean(time_measures),
        }

        print('....')
        print('PASSED')

        del get_weight_paths, predict
        del sys.modules["pyx_endpoints"]

        from gc import collect
        collect()

        sys.path.pop()
    except Exception as e:
        print(e.with_traceback())
        print('....')
        print('An error occurred.')
        return False

    return True


@ensure_pyx_project
def run_locally(args, pyx_project, extra_fields, **kwargs):
    import os
    import time
    import sys

    input_dir = args.input_dir
    output_dir = args.output_dir

    os.makedirs(output_dir, exist_ok=True)

    try:
        sys.path.append('.')
        from pyx_endpoints import get_weight_paths, predict

        print('Testing model ...')
        print('Initializing model ...')
        weight_paths = {i: k for i, k in get_weight_paths().items()}
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
        del sys.modules["pyx_endpoints"]

        from gc import collect
        collect()

        sys.path.pop()
    except Exception as e:
        print(e.with_traceback())
        print('....')
        print('An error occurred.')
        return False


@with_pyx_config
@ensure_pyx_project
def publish(args, pyx_project, pyx_config, **kwargs):
    import requests
    from urllib.parse import urljoin

    if os.path.exists('./pyx-web/description.md'):
        with open('./pyx-web/description.md', 'r') as f:
            pyx_project['description_full'] = f.read()
            f.close()

    if 'id' in pyx_project:
        print('Updating project:')
        headers = {'Content-type': 'application/json', 'user-token': pyx_config["user_token"]}
        r = requests.put(urljoin(__PYX_CONFIG__["api_url"], 'models/' + str(pyx_project['id'])), headers=headers, json=pyx_project)
    else:
        headers = {'Content-type': 'application/json', 'user-token': pyx_config["user_token"]}
        r = requests.post(urljoin(__PYX_CONFIG__["api_url"], 'models'), headers=headers, json=pyx_project)

    print('After verification you can call the following to make your listing available:')
    print('$ pyx publish --make-available true')

    try:
        for k in r.json():
            pyx_project[k] = r.json()[k]

        _save_config(pyx_config)
        upload(args, pyx_project=pyx_project)

        if 'make_available' in kwargs['extra_fields']:
            r = requests.put(urljoin(__PYX_CONFIG__["api_url"], 'models/' + str(pyx_project['id']) + '/publish'),
                             headers=headers, json={})
            print(r.status_code)
    except:
        pass


@with_pyx_config
@ensure_pyx_project
@ensure_have_permissions
def upload(args, pyx_project, pyx_config, **kwargs):
    import requests
    from urllib.parse import urljoin
    import os
    import tempfile

    with tempfile.TemporaryDirectory() as tmpdirname:
        print('Packing current project ...')
        import tarfile
        import os.path

        def make_tarfile(output_filename, source_dir):
            with tarfile.open(output_filename, "w") as tar:
                for f in os.listdir():
                    dir_name = f
                    if f not in ['pyx-web', 'pyx-testing-data']:
                        dir_name = 'models/' + pyx_project['framework'] + '/' + dir_name
                    tar.add(os.path.join(source_dir, f), arcname=dir_name)

        make_tarfile(os.path.join(tmpdirname, '_project.tar'), '.')

        print('Uploading data ...')
        model_id = str(pyx_project['id'])
        headers = {'user-token':  pyx_config["user_token"],
                   'Content-Type': 'application/octet-stream'}

        fileobj_it = UploadInChunks(os.path.join(tmpdirname, '_project.tar'), 1024 * 1024 * 16)
        r = requests.post(urljoin(__PYX_CONFIG__["api_url"], 'models/' + model_id + '/upload'),
                          headers=headers,
                          data=fileobj_it)

        if r.status_code == 200:
            print('Successfully uploaded.')
        else:
            print(r.status_code)
            print('An error occurred.')


@with_pyx_config
def download(args, pyx_config, **kwargs):
    import requests
    from urllib.parse import urljoin
    import shutil
    import os
    import tempfile

    version = 'latest'
    model_id = args.model_name
    if model_id.find(':') != -1:
        model_id, version = model_id.split(':')

    print('Downloading data ...')

    headers = {'user-token':  pyx_config["user_token"]}
    r = requests.get(urljoin(__PYX_CONFIG__["api_url"], 'models/' + model_id + '/download/' + version),
                     headers=headers, stream=True)

    if r.status_code == 200:
        print('Successfully pulled ...')
    else:
        print('An error occurred.')
        return

    with tempfile.TemporaryDirectory() as tmpdirname:
        print('Unpacking current project ...')
        with open(os.path.join(tmpdirname, '_project.tar'), 'wb') as out_file:
            shutil.copyfileobj(r.raw, out_file)

        os.makedirs(args.project_name, exist_ok=True)
        import tarfile
        tar = tarfile.open(os.path.join(tmpdirname, '_project.tar'))
        tar.extractall(path=args.project_name)
        tar.close()

        print('....')
        print('DONE')


@with_pyx_config
def cloud_run(args, extra_fields, pyx_config, **kwargs):
    import requests
    from urllib.parse import urljoin
    import shutil
    import os
    import tempfile

    model_id, framework = args.model_name.split('/')
    version = 'latest'
    if framework.find(':') != -1:
        framework, version = framework.split(':')

    def base64_encode_file(file_to_encode):
        import base64
        return base64.b64encode(open(file_to_encode, 'rb').read())

    def from_base64(base64_data, output_file):
        import base64
        with open(output_file, 'wb') as f:
            f.write(base64.decodebytes(str.encode(base64_data)))
            f.close()

    with tempfile.TemporaryDirectory() as tmpdirname:
        print('Packing current input directory ...')
        shutil.make_archive(os.path.join(tmpdirname, '_input_files'), 'zip', args.input_dir)

        print('Uploading data ...')

        headers = {'user-token': pyx_config["user_token"]}

        fileobj_it = UploadInChunks(os.path.join(tmpdirname, '_input_files.zip'), 1024 * 1024 * 1)
        r = requests.post(urljoin(__PYX_CONFIG__["api_url"], 'tasks/enqueue/' + model_id + '/' + framework + '/' + version),
                          headers=headers,
                          data=fileobj_it)

        if r.status_code != 200:
            print(r.json()['status_msg'])
            print('An error occurred.')
            return

        task_id = r.json()['task_id']
        print('Assigned task id {0}...'.format(task_id))
        print()
        print('Polling for data to be processed...')

        while True:
            headers = {'user-token': pyx_config["user_token"]}
            r = requests.get(
                urljoin(__PYX_CONFIG__["api_url"], 'tasks/status/' + str(task_id)),
                headers=headers)
            res = r.json()
            print('\x1b[2K' + 'current status: ' + str(res['status']), end='\r')

            if res['result']:
                break

        print()

        if r.status_code == 200:
            print('Successfully predicted.')
            print('Unpacking results ...')

            from_base64(res['result']['output_dir'], os.path.join(tmpdirname, '_output_files.zip'))
            shutil.unpack_archive(os.path.join(tmpdirname, '_output_files.zip'), args.output_dir)
        else:
            print(r.content)
            print('An error occurred.')

    pass


@with_pyx_config
def quotas(args, pyx_config, **kwargs):
    import requests
    from urllib.parse import urljoin

    headers = {'user-token': pyx_config["user_token"]}
    r = requests.get(urljoin(__PYX_CONFIG__["api_url"], 'quotas/'), headers=headers)

    if r.status_code == 200:
        print('Requests left: ', r.json()['requests'])
    else:
        print('An error occurred. User is not registered or auth-token is broken. Try "pyx auth <token> first.')
        return


@with_pyx_config
def users_remote_models(args, pyx_config, **kwargs):
    import requests
    from urllib.parse import urljoin

    headers = {'user-token': pyx_config["user_token"]}
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
        print('An error occurred. User is not registered or auth-token is broken. Try "pyx auth <token> first.')
        return


def main():
    parser = argparse.ArgumentParser(prog='pyx')

    subparsers = parser.add_subparsers(dest='mode', help='sub-command help')

    parser_auth = subparsers.add_parser('auth', help='Auth PYX user')
    parser_auth.add_argument('user_token', type=str, help='set user token')

    parser_create = subparsers.add_parser('create', help='Create a new PYX project (using wizard)')
    parser_attach = subparsers.add_parser('attach', help='Attach model to existing PYX project (using wizard)')
    parser_configure = subparsers.add_parser('configure', help='Create a config file for a PYX project')

    parser_download = subparsers.add_parser('download', help='Pull a published workspace')
    parser_download.add_argument('model_name', type=str, help='model id / framework from pyx.ai')
    parser_download.add_argument('project_name', type=str, help='destination project name')

    parser_publish = subparsers.add_parser('publish', help='Publish a project to pyx.ai')
    parser_upload = subparsers.add_parser('upload', help='Upload current workspace to pyx.ai')

    parser_cloud_run = subparsers.add_parser('cloud-run', help='Run model using pyx.ai cloud')
    parser_cloud_run.add_argument('model_name', type=str, help='a model path from pyx.ai (model-id/framework:version)')
    parser_cloud_run.add_argument('input_dir', type=str, help='directory with input samples')
    parser_cloud_run.add_argument('output_dir', type=str, help='directory with results')

    parser_run = subparsers.add_parser('run', help='Perform inference locally')
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

    extra_params, unknown = extra_fields_parser.parse_known_args()

    subprogs = {
        'auth': auth,
        'create': create,
        'attach': attach,
        'configure': configure,
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
