"""
Template Module
"""

import jinja2

def __get_env(path):
    templateLoader = jinja2.FileSystemLoader( searchpath=path )
    templateEnv = jinja2.Environment( loader=templateLoader )
    return templateEnv

def template_container_dockerfile(config, container):
    """
    Returns the contents of the specified container's Dockerfile,
    with the dictionary of template values applied.
    """
    template_dict = config.test_vars    
    template_dict.update({'container_name':container})
    dockerfilepath = "/containers/"+container+"/XShopfile"
    Templater = __get_env(config.project_directory)
    template = Templater.get_template(dockerfilepath)
    return template.render(template_dict)
