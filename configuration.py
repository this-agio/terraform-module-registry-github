
import yaml
def read_configuration(configuration_file):
    config = yaml.load(open(configuration_file, 'r'), Loader=yaml.FullLoader)
    modules = {}
    for module in config['modules']:
        namespace = modules.setdefault(module['namespace'], {})
        name = namespace.setdefault(module['name'], {})
        system = name.setdefault(module['system'], module)
    return modules