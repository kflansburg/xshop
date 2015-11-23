"""Provider Support Module
        
Provides useful methods for providers to construct the build context. 
"""

import os
from xshop import template
from xshop import exceptions
import subprocess

class Helper:
    """
    Object with some helpful methods for manipulating context. 
    """
    
    config = None

    def __init__(self, config):
        self.config = config

    def read(self, container, provider):
        """
        Reads a container's XShopFile, applies a template and parses the file
        into a list of verbs and list of arguments with no FROM tags. 
        Determines the appropriate FROM tag, and returns this as well. 
        """
        
        dockerfile = template.template_container_dockerfile(
            self.config, 
            container)

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

        # Determine FROM
        providerfrom = "FROM_"+provider.upper()
        baseimage=None
        if "FROM" in verbs:
            baseimage = arguments[verbs.index('FROM')]
        if providerfrom in verbs:
            baseimage = arguments[verbs.index(providerfrom)]
        if baseimage==None:
            raise exceptions.ProviderError("No FROM statement found.")

        # Filter out FROM statements
        [verbs,arguments] = [list(t) for t in zip(
            *filter(lambda v: not "FROM" in v[0], zip(verbs,arguments)))]
        
        return [baseimage, verbs, arguments]

    def copypackages(self, container):
        """
        Copies packages into current folder, if required.
        """
        if self.config.test_vars['install_type'] == 'debian' and container=='target':
           subprocess.call(['cp','-p','-r',self.config.packages_path,'.'])

    def copysource(self, container):
        """
        Copies the requires source file into the current directory if
        required.
        """
        if self.config.test_vars['install_type'] == 'source' and container=='target':
            subprocess.call('cp -p "%s"* .'%(self.config.source_path,),shell=True)


    def copycontext(self, container):
        """
        Copies contents of container build context into current folder.
        """
        context = self.config.containers[container]['build_files_directory']
        subprocess.call('cp -r -p "%s/"* .'%(context,),shell=True)

    def copytestfiles(self):
        """
        Copies contents of test folder into current folder. 
        """
        subprocess.call(['cp','-r','-p',self.config.test_directory,'.']) 
