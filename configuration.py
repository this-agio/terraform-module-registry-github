
import sys
import yaml


def read_configuration(configuration_file):
    modules_configuration = yaml.load(open(configuration_file, 'r'), Loader=yaml.FullLoader)
    config = {
        'semver_regexp': '(?P<version>(?P<major>0|[1-9]\\d*)\\.(?P<minor>0|[1-9]\\d*)\\.(?P<patch>0|[1-9]\\d*)(?:-(?P<prerelease>(?:0|[1-9]\\d*|\\d*[a-zA-Z-][0-9a-zA-Z-]*)(?:\\.(?:0|[1-9]\\d*|\\d*[a-zA-Z-][0-9a-zA-Z-]*))*))?(?:\\+(?P<buildmetadata>[0-9a-zA-Z-]+(?:\\.[0-9a-zA-Z-]+)*))?)',
        'modules': {}
    }
    for module in modules_configuration['modules']:
        namespace = config['modules'].setdefault(module['namespace'], {})
        name = namespace.setdefault(module['name'], {})
        system = name.setdefault(module['system'], module)
    return config


config = read_configuration(sys.argv[1])


def find_module(namespace, name, system):
    namespace = config['modules'].get(namespace) or {}
    name = namespace.get(name) or {}
    return name.get(system)
