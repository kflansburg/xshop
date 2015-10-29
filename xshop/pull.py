"""
Pull Module

Automatic downloading of source files based on config.yaml
"""

from subprocess import call as sh
from xshop import colors as clr
from xshop import config
import re
import os

def __generate_urls(urls):
    """
    Expands URL lists.
    """
    REGEX = '([^{}]+)({.+})([^{}]*)'
    r = re.compile(REGEX)
    results = []    
    for url in urls:
        g = r.match(url)
        if g:
            var = g.group(2)[1:-1].split(',')
            for v in var:
                u = list(g.groups())
                u[1]=v
                results.append("".join(u))
        else:
            results.append(url)
    return results

def __download(url):
    """
    Downloads a given URL and attempts to verify it.
    """
    print clr.BOLD+"Downloading:\t%s"%(url)+clr.ENDC
    devnull=open(os.devnull,'w')
    
    # Attempt to download file
    if sh(['wget','-N',url],stderr=devnull):
        print clr.FAIL+"FAILED"+clr.ENDC
        return 1
    
    else:
        print clr.OKGREEN+"Success"+clr.ENDC
    
        # Attempt to download .asc
        if (sh(['wget',
                '-N',
                url+".asc"],
                stderr=devnull,
                stdout=devnull) and 
            sh(['wget',
                '-N',
                url+".sig"],
                stderr=devnull,
                stdout=devnull) and 
            sh(['wget',
                '-N',
                url+".sig.asc"],
                stderr=devnull,
                stdout=devnull)):
            
            print (clr.WARNING
                    + "No signing file found, looking for hashes."
                    + clr.ENDC)
            
            f = url.split('/')[-1]
            folder = '/'.join(url.split('/')[:-1])+"/CHECKSUMS"
            
            
            if (sh(['wget',
                    '-N',
                    url+".md5"],
                    stderr=devnull,
                    stdout=devnull) and 
                sh('curl '+folder+' | grep '+f+' > '+f+'.md5',
                    stderr=devnull,
                    stdout=devnull,shell=True)):
                
                print (clr.WARNING
                    + "No MD5"
                    + clr.ENDC)
            else:
                
                print (clr.OKGREEN
                        + "MD5 Found!"
                        + clr.ENDC )
                return 3
            
            if sh(['wget',
                    '-N',
                    url+".sha1"],
                    stderr=devnull,
                    stdout=devnull):
                print(clr.WARNING
                    + "No SHA1"
                    + clr.ENDC )
                return 5
            else:
                print (clr.OKGREEN
                    + "SHA1 Found!"
                    + clr.ENDC )
                return 4

        else:
            print (clr.OKGREEN
                + "Signing file found!"
                + clr.ENDC)
            return 0 

def __verify(u):
    """
    Verifies a given file with GPG.
    """

    f = u.split('/')[-1]
    devnull=open(os.devnull,'w')

    if (sh(['gpg',
            '--verify',
            f+".asc"],
            stdout=devnull,
            stderr=devnull) and 
        sh(['gpg',
            '--verify',
            f+".sig"],
            stdout=devnull,
            stderr=devnull)):

        print (clr.WARNING
            + "Verification Failed!"
            + clr.ENDC)
        return 1
    else:
        print (clr.OKGREEN
            + "Verified"
            + clr.ENDC)
 
def __check_sha1(u):
    """
    Checks a file with SHA-1
    """

    f = u.split('/')[-1]+".sha1"
    if sh(['sha1sum','-c',f]):
        print(clr.WARNING
            + "SHA1 Verification Failed!"
            + clr.ENDC)
        return 1
    else:
        print(clr.OKGREEN
            + "SHA1 Verified"
            + clr.ENDC)

def ___check_md5(u):
    """
    Checks a given file with MD5
    """

    f = u.split('/')[-1]+".md5"

    if sh(['md5sum','-c',f]):
        print(clr.WARNING
            + "MD5 Verification Failed!"
            + clr.ENDC)
        return 1
    else:
        print(clr.OKGREEN
            + "MD5 Verified"
            + clr.ENDC)

def pull():
    """
    Pulls files associated with a given project.
    """

    c = config.Config({'version':'blah'})

    urls = c.config['source']
    print "Source URLS:"
    urls = __generate_urls(urls)
    for u in urls:
        print u
    try:
        keys = c.config['public_keys']
        print "Public Keys:"
        print(clr.WARNING
            + "THESE MUST BE ADDED MANUALLY"
            + clr.ENDC)
	print "gpg  --keyserver pgp.mit.edu --send-keys <key-id>"
        for k in c.config['public_keys']:
            print k
    except KeyError:
        print "No public keys mentioned"

    rootdir = os.getcwd()
    if not os.path.isdir('source'):
        os.mkdir('source')
    
    os.chdir('source')
    
    failed = False
    verifyfail = False
    for u in urls:
        ret = __download(u)
        if ret==1:
            failed = True
        elif ret==0:
            if __verify(u):
                verifyfail=True
        elif ret==3:
            if __check_md5(u):
                verifyfail=True
        elif ret==4:
            if __check_sha1(u):
                verifyfail=True
    os.chdir(rootdir)
    

    if failed:
        print(clr.FAIL
            + "One or more files could not be retrieved!"
            + clr.ENDC)
    if verifyfail:
        print(clr.WARNING
            + "One or more of the file verifications failed!"
            + clr.ENDC)
    
    try:
        notes = c.config['notes']
        print clr.OKBLUE+notes+clr.ENDC
    except KeyError:
        print clr.KBLUE+"No Notes."+clr.ENDC
