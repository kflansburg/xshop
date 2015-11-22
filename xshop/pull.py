"""
Pull Module

Automatic downloading of source files based on config.yaml
"""

from subprocess import call as sh
from xshop import colors as clr
from xshop import config
import re
import os
import json
import urllib2
from cStringIO import StringIO
import tarfile
import shutil
import itertools
import copy

def __expand_url(url):
    """
    Expands the tuples in a single url.
    """
    a = re.split('\{([^\{\}]+)\}',url)
    strings = a[0:][::2]
    lists = a[1:][::2]
    lists = map(lambda v: v.split(','), lists)
    lists = list(itertools.product(*lists))
    results = []
    for combination in lists:
        result = [None]*(len(strings)+len(combination))
        result[::2] = strings
        result[1::2] = combination
        results += [''.join(result)]
    return results

def __generate_urls(urls):
    """
    Expands the list of URLs for each path. 
    """
    for k,v in urls.iteritems():
        l = []
        for url in v:
            l+= __expand_url(url)
        urls[k] = l
        
    return urls

def __download_file(url):
    try:
        response = urllib2.urlopen(url)
        filename = response.url.split('/')[-1]
        f = open(filename,'w')
        f.write(response.read())
        f.close()
        return 0
    except urllib2.HTTPError:
        return 1

def __download_url(url):
    """
    Downloads a given URL and attempts to verify it.
    """
    
    print clr.BOLD+"Downloading:\t%s"%(url)+clr.ENDC
    if __download_file(url):
        print clr.FAIL+"FAILED"+clr.ENDC
        return 1
    
    print clr.OKGREEN+"Success"+clr.ENDC
    if not (__download_file(url+".asc") and 
        __download_file(url+".sig")):
        print (clr.OKGREEN
            + "Signing file found!"
            + clr.ENDC)
        return 0 

    print (clr.WARNING
        + "No signing file found, looking for hashes."
        + clr.ENDC)
 
    filename = url.split('/')[-1]
    folder = '/'.join(url.split('/')[:-1])

    if not __download_file(url+".md5"):
        print (clr.OKGREEN
            + "MD5 Found!"
            + clr.ENDC )
        return 3

    print (clr.WARNING
        + "No MD5"
        + clr.ENDC)
    
    if not __download_file(url+".sha1"):
        print (clr.OKGREEN
            + "SHA1 Found!"
            + clr.ENDC )
        return 4

    else:
        print (clr.WARNING
            +"NO SHA1"
            +clr.ENDC)
        return 5

def __verify(u):
    """
    Verifies a given file with GPG.
    """

    f = u.split('/')[-1]
    devnull=open(os.devnull,'w')

    results = 0
    try:
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
            results = 1
        else:
            print (clr.OKGREEN
                + "Verified"
                + clr.ENDC)

    except OSError:
        print clr.WARNING + "GPG not found on system."+clr.ENDC
        results = 1
    finally:
        # Remove any verification files
        if os.path.isfile(f+".sig"):
            os.remove(f+".sig")
        if os.path.isfile(f+".asc"):
            os.remove(f+".asc")
        return results

def __check_sha1(u):
    """
    Checks a file with SHA-1
    """
    try:
        f = u.split('/')[-1]+".sha1"
        results = 0
        if sh(['sha1sum','-c',f]):
            print(clr.WARNING
                + "SHA1 Verification Failed!"
                + clr.ENDC)
            results = 1
        else:
            print(clr.OKGREEN
                + "SHA1 Verified"
                + clr.ENDC)

    except OSError:
        print clr.WARNING + "sha1sum not found on system."+clr.ENDC
        results =  1
    finally:
        if os.path.isfile(f):
            os.remove(f)
        return results

def ___check_md5(u):
    """
    Checks a given file with MD5
    """
    try:
        f = u.split('/')[-1]+".md5"
        results = 0
        if sh(['md5sum','-c',f]):
            print(clr.WARNING
                + "MD5 Verification Failed!"
                + clr.ENDC)
            results = 1
        else:
            print(clr.OKGREEN
                + "MD5 Verified"
                + clr.ENDC)

    except OSError:
        print clr.WARNING+"md5sum not found on system."+clr.ENDC
        results =  1
    finally:
        if os.path.isfile(f):
                os.remove(f)
        return results

def __resolve_ambiguous_id(data):
    """
    Prints a table of project search results and asks that the 
    user specify a project to use.
    """
    ln = max(map(lambda project: len(project['name']),data))
    ll = max(map(lambda project: len(project['library']),data))
    print clr.BOLD+ "Multiple Matches Found" + clr.ENDC
    print clr.HEADER+"No\t"+"Name".ljust(ln)+"\t"+"Library".ljust(ll)+"\t\t"+"CVE(s)"+clr.ENDC
    for idx,project in enumerate(data):
        print clr.WARNING+str(idx)+")\t"+clr.ENDC,
        print clr.OKGREEN+project['name'].ljust(ln)+"\t"+clr.ENDC,
        print clr.OKBLUE+project['library'].ljust(ll)+"\t"+clr.ENDC,
        print project['cve']
    selection = raw_input('Enter the number of your selection: ')

    try: 
        selection = int(selection)
        if selection < 0 or selection>len(data)-1:
            print clr.BOLD+"Invalid Selection"+clr.ENDC
            return resolve_ambiguous_id(data)
        else:
            return data[selection]

    except ValueError:
        print clr.BOLD+"Invalid Selection"+clr.ENDC
        return resolve_ambiguous_id(data)


def __download_project(project):
    """
    Downloads a given project, untars it, and pulls the
    source files specified in config.yaml
    """
    print clr.BOLD+"Downloading %s"%(project['name'])+clr.ENDC
    response = urllib2.urlopen(project['download_url'])
    print clr.BOLD+"Extracting %s"%(project['name'])+clr.ENDC
    tar = tarfile.open(mode= "r:gz", fileobj = StringIO(response.read()))
    folder = tar.getmembers()[0].name
    tar.extractall()
    name = project['name']
    shutil.move(folder, name)
    current_dir = os.getcwd()
    os.chdir(name)
    print clr.BOLD+"Pulling %s Files"%(project['name'])+clr.ENDC
    pull_local_project()
    os.chdir(current_dir)
 

def pull_from_site(key):
    """
    Searches xshop.gtisc.gatech.edu for the given project ID 
    and downloads the project files. If multiple matching ID's
    are found, the user is asked to clarify. 
    """
    response = urllib2.urlopen('https://xshop-site.herokuapp.com/search.json?q=%s'%(key,))
    data = json.loads(response.read())
    if len(data)>1:
        project = __resolve_ambiguous_id(data)
    else:
        project = data[0]

    __download_project(project)

FAILED=False
VERIFYFAIL=False

def __download_and_verify(url):
    """
    Fetches each file, and attempts to verify it based on
    the verification file type found.
    """
    
    n = __download_url(url)
    if n==1:
        FAILED = True
    elif n==0:
        if __verify(url):
            VERIFYFAIL=True
    elif n==3:
        if __check_md5(url):
            VERIFYFAIL=True
    elif n==4:
        if __check_sha1(url):
            VERIFYFAIL=True

def pull_local_project():
    """
    Pulls files associated with a given project.
    """

    c = config.Config({'version':'blah'})

    try:
        urls = c.config['files']
        print "Source URLS:"
        urls = __generate_urls(urls)

        project_directory = os.getcwd()

        for path, files in urls.iteritems():
            try:
                os.makedirs(path)
            except os.error:
                pass

            os.chdir(path)

            for url in files:
                __download_and_verify(url)

            os.chdir(project_directory)

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

        
        verifyfail = False
       

        if FAILED:
            print(clr.FAIL
                + "One or more files could not be retrieved!"
                + clr.ENDC)
        if VERIFYFAIL:
            print(clr.WARNING
                + "One or more of the file verifications failed!"
                + clr.ENDC)
    except KeyError:
        print clr.BOLD+"No File to Download."+clr.ENDC
 
    try:
        notes = c.config['notes']
        print clr.OKBLUE+notes+clr.ENDC
    except KeyError:
        print clr.OKBLUE+"No Notes."+clr.ENDC

def files():
    c = config.Config({'version':'blah'})
    urls = c.config['files']
    urls = __generate_urls(urls)
    for k,v in urls.iteritems():
        urls[k] = map(lambda u: u.split("/")[-1],urls[k])
    return urls

def pull(key=None):
    if key: 
        pull_from_site(key)
    else:
        pull_local_project()
