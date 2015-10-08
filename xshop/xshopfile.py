"""
XShopfile Module
        
    Provides methods for reading and parsing XShopfiles
"""

import os
from xshop import template

def read(config, container):
    """
    Reads a container's XShopfile, applies a template and parses the file
    into a list of (verb,argument) tuples. 
    """
    
    template_dict = config.test_vars

    dockerfile = template.template_container_dockerfile(config, container, template_dict)

    # Split by line
    dockerfile = dockerfile.split('\n')
    dockerfile = map(lambda l: l.strip(), dockerfile)
    
    # Remove Comments and Newlines
    dockerfile = filter(lambda l: not l=="", dockerfile)
    dockerfile = filter(lambda l: not l[0]=="#", dockerfile)

    # Split Verbs and Arguments
    dockerfile = map(lambda l: l.split(" ",1), dockerfile) 
    verbs = map(lambda l: l[0], dockerfile)
    arguments = map(lambda l: l[1], dockerfile) 

    return [verbs, arguments]

