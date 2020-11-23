import argparse


__PYX_CONFIG__ = {
    'api_url': 'https://beta.pyx.ai/api/'
}


def _load_config():
    """
    Load JSON config from ~/.pyx/pyx.json
    """
    import os
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


def auth(args):
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


def create(args):
    """
    Create new project
    """
    import os
    import pyx

    pyx_boilerplates_path = os.path.join(os.path.dirname(pyx.__file__), 'boilerplates', args.category)

    if os.path.exists(pyx_boilerplates_path):
        print('Creating project ...')
        try:
            from shutil import copytree
            copytree(pyx_boilerplates_path, args.project_name)
            print('...')
            print('Your boilerplate is ready to use. Please, run:')
            print('$ cd ' + args.project_name)
            print('$ python PYX.py')
        except FileExistsError:
            print('Destination directory is already exist. Consider another name of the project.')

    else:
        print('Template {0} not found'.format(args.category))


def test(*args, **kwargs):
    """
    Test model
    """
    import os
    import time
    import numpy as np

    if not os.path.exists('PYX.py'):
        print('Cant find PYX.py. Are you in a pyx-project directory?')
        return False
    else:
        try:
            print('Testing project ...')
            import sys
            sys.path.append('./')
            from PYX import PYXImplementedModel

            print('Initializing model ...')
            project = PYXImplementedModel()
            project.initialize()
            project.set_weights()

            print('inputs: ', project.get_input_shapes())
            print('inputs: ', project.get_input_types())
            print('....')

            for i in range(10):
                test_sample = {}
                inputs = project.get_input_shapes()

                for k in inputs:
                    test_sample[k] = np.zeros(inputs[k])

                start = time.time()
                _ = project.predict(test_sample)
                end = time.time()
                print('Inference time: ', end - start)

            print('....')
            print('PASSED')
        except:
            print('....')
            print('An error occured.')
            return False

        return True


def push(args, **kwargs):
    if not test():
        print('Can not submit without testing first.')

    import requests
    from urllib.parse import urljoin
    import shutil
    import os
    import tempfile

    with tempfile.TemporaryDirectory() as tmpdirname:
        print('Packing current project ...')
        shutil.make_archive(os.path.join(tmpdirname, '_project'), 'zip', '.')

        print('Uploading data ...')
        model_id, framework = args.model_name.split('/')
        fileobj = open(os.path.join(tmpdirname, '_project.zip'), 'rb')
        headers = {'user-token':  __PYX_CONFIG__["user_token"]}
        r = requests.post(urljoin(__PYX_CONFIG__["api_url"], 'model/' + model_id + '/upload/' + framework),
                          headers=headers,
                          files={"project_files": ("project.zip", fileobj)})

        if r.status_code == 200:
            print('Succesfully pushed.')
        else:
            print('An error occured.')


def pull(args, **kwargs):
    import requests
    from urllib.parse import urljoin
    import shutil
    import os
    import tempfile

    print('Downloading data ...')
    model_id, framework = args.model_name.split('/')

    headers = {'user-token':  __PYX_CONFIG__["user_token"]}
    r = requests.get(urljoin(__PYX_CONFIG__["api_url"], 'model/' + model_id + '/download/' + framework),
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

        shutil.unpack_archive(os.path.join(tmpdirname, 'src.zip'), model_id)

        print('....')
        print('DONE')


def predict(args, **kwargs):
    print(args, kwargs)
    import requests
    from urllib.parse import urljoin
    import shutil
    import os
    import tempfile
    import json
    model_id, framework = args.model_name.split('/')

    headers = {'user-token':  __PYX_CONFIG__["user_token"]}
    r = requests.post(urljoin(__PYX_CONFIG__["api_url"], 'model/' + model_id + '/predict/' + framework),
                     headers=headers)

    if r.status_code == 200:
        print('Succesfully predicted ...')
    else:
        print('An error occured.')
        return


def main():
    _load_config()
    print(__PYX_CONFIG__)
    parser = argparse.ArgumentParser(prog='pyx')

    subparsers = parser.add_subparsers(dest='mode', help='sub-command help')

    parser_auth = subparsers.add_parser('auth', help='Auth PYX user')
    parser_auth.add_argument('user_token', type=str, help='set user token')

    parser_create = subparsers.add_parser('create', help='Create new PYX project')
    parser_create.add_argument('project_name', type=str, help='a name of new project (e.g. resnet-test)')
    parser_create.add_argument('category', type=str, help='a category of a new project (e.g. cv/classification)')

    parser_pull = subparsers.add_parser('pull', help='Pull published workspace')
    parser_pull.add_argument('model_name', type=str, help='a magic url from pyx.ai')

    parser_push = subparsers.add_parser('push', help='Push current workspace to pyx.ai')
    parser_push.add_argument('model_name', type=str, help='a magic url from pyx.ai (model-id/framework)')

    parser_predict = subparsers.add_parser('predict', help='Push current workspace to pyx.ai')
    parser_predict.add_argument('model_name', type=str, help='a magic url from pyx.ai (model-id/framework)')

    _ = subparsers.add_parser('test', help='Run tests locally')

    # params = parser.parse_args()

    params, unknown = parser.parse_known_args() # this is an 'internal' method
    # which returns 'parsed', the same as what parse_args() would return
    # and 'unknown', the remainder of that
    # the difference to parse_args() is that it does not exit when it finds redundant arguments

    for arg in unknown:
        if arg.startswith(("-", "--")):
            # you can pass any arguments to add_argument
            parser_predict.add_argument(arg, type=str)

    params = parser.parse_args()

    subprogs = {
        'auth': auth,
        'create': create,
        'test': test,
        'push': push,
        'pull': pull,
        'predict': predict,
    }

    subprogs[params.mode](params)
