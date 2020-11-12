import argparse


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


def main():
    parser = argparse.ArgumentParser(prog='pyx')

    subparsers = parser.add_subparsers(dest='mode', help='sub-command help')

    parser_create = subparsers.add_parser('create', help='Create new PYX project')
    parser_create.add_argument('project_name', type=str, help='a name of new project (e.g. resnet-test)')
    parser_create.add_argument('category', type=str, help='a category of a new project (e.g. cv/classification)')

    parser_pull = subparsers.add_parser('pull', help='Pull published workspace')
    parser_pull.add_argument('magic-url', type=str, help='a magic url from pyx.ai')

    parser_push = subparsers.add_parser('push', help='Push current workspace to pyx.ai')
    parser_push.add_argument('magic-url', type=str, help='a magic url from pyx.ai')

    _ = subparsers.add_parser('test', help='Run tests locally')

    params = parser.parse_args()

    subprogs = {
        'create': create
    }

    subprogs[params.mode](params)
