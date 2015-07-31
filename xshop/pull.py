#
#   Pull
#
#       Automatic downloading of source files based on config.yaml
#
#

from xshop import config
import re
from subprocess import call as sh
import os
from xshop import colors
def generate_urls(urls):
    REGEX = '([^{}]+)({.+})([^{}]+)'
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

def download(url):
    print colors.colors.BOLD+"Downloading:\t%s"%(url)+colors.colors.ENDC
    devnull=open(os.devnull,'w')
    # Attempt to download file
    if sh(['wget','-N',url],stderr=devnull):
        print colors.colors.FAIL+"FAILED"+colors.colors.ENDC
        return 1
    else:
        print colors.colors.OKGREEN+"Success"+colors.colors.ENDC
        # Attempt to download .asc
        if sh(['wget','-N',url+".asc"],stderr=devnull,stdout=devnull) and sh(['wget','-N',url+".sig"],stderr=devnull,stdout=devnull) and sh(['wget','-N',url+".sig.asc"],stderr=devnull,stdout=devnull):
            print colors.colors.WARNING+"No signing file found, looking for hashes."+colors.colors.ENDC
            f = url.split('/')[-1]
            folder = '/'.join(url.split('/')[:-1])+"/CHECKSUMS"
            if sh(['wget','-N',url+".md5"],stderr=devnull,stdout=devnull) and sh('curl '+folder+' | grep '+f+' > '+f+'.md5',stderr=devnull,stdout=devnull,shell=True):
                print colors.colors.WARNING+"No MD5"+colors.colors.ENDC 
            else:
                print colors.colors.OKGREEN+"MD5 Found!"+colors.colors.ENDC 
                return 3
            if sh(['wget','-N',url+".sha1"],stderr=devnull,stdout=devnull):
                print colors.colors.WARNING+"No SHA1"+colors.colors.ENDC 
                return 5
            else:
                print colors.colors.OKGREEN+"SHA1 Found!"+colors.colors.ENDC 
                return 4

        else:
            print colors.colors.OKGREEN+"Signing file found!"+colors.colors.ENDC
            return 0 

def verify(u):
    f = u.split('/')[-1]
    devnull=open(os.devnull,'w')
    if sh(['gpg','--verify',f+".asc"],stdout=devnull,stderr=devnull) and sh(['gpg','--verify',f+".sig"],stdout=devnull,stderr=devnull):
        print colors.colors.WARNING+"Verification Failed!"+colors.colors.ENDC
        return 1
    else:
        print colors.colors.OKGREEN+"Verified"+colors.colors.ENDC
 
def check_sha1(u):
    f = u.split('/')[-1]+".sha1"
    if sh(['sha1sum','-c',f]):
        print colors.colors.WARNING+"SHA1 Verification Failed!"+colors.colors.ENDC
        return 1
    else:
        print colors.colors.OKGREEN+"SHA1 Verified"+colors.colors.ENDC

def check_md5(u):
    f = u.split('/')[-1]+".md5"
    if sh(['md5sum','-c',f]):
        print colors.colors.WARNING+"MD5 Verification Failed!"+colors.colors.ENDC
        return 1
    else:
        print colors.colors.OKGREEN+"MD5 Verified"+colors.colors.ENDC

def pull():
    c = config.Config()
    urls = c.get('source')
    print "Source URLS:"
    urls = generate_urls(urls)
    for u in urls:
        print u
    try:
        keys = c.get('public_keys')    
        print "Public Keys:"
        print colors.colors.WARNING+"THESE MUST BE ADDED MANUALLY"+colors.colors.ENDC
        for k in c.get('public_keys'):
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
        ret = download(u)
        if ret==1:
            failed = True
        elif ret==0:
            if verify(u):
                verifyfail=True
        elif ret==3:
            if check_md5(u):
                verifyfail=True
        elif ret==4:
            if check_sha1(u):
                verifyfail=True
    os.chdir(rootdir)
    

    if failed:
        print colors.colors.FAIL+"One or more files could not be retrieved!"+colors.colors.ENDC
    if verifyfail:
        print colors.colors.WARNING+"One or more of the file verifications failed!"+colors.colors.ENDC
    
    try:
        notes = c.get('notes')
        print colors.colors.OKBLUE+notes+colors.colors.ENDC
    except KeyError:
        print colors.colors.OKBLUE+"No Notes."+colors.colors.ENDC
