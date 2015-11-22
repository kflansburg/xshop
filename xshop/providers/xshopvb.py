"""
    VirtualBox Wrapper Module

        Exposes methods for constructing test environments with VirtualBox
"""

from xshop import template
from xshop import psupport
from xshop import exceptions
from xshop import sh
from xshop import colors as clr
from subprocess import *
import json
import logging
import hashlib
import os
import time
import copy



def list_vms():
    """
    Returns a dictionary of VM's and thier UUIDs
    """

    p = Popen(['VBoxManage','list','vms'],stdout=PIPE)
    vms = {}
    list_results = p.stdout.readlines()
    for line in list_results:
        vms[" ".join(line.split(" ")[0:-1]).strip('{}"\n')]=line.split(" ")[-1].strip('{}"\n')

    return vms

def check_for_virtualbox():
    """
    Confirms that VBoxManage is available
    """
    try:
        call(['VBoxManage'],stdout=PIPE)
        return True
    except OSError:
        return False

def vboxmanage(command,error_message):
    p = Popen(['VBoxManage']+command,stdout=PIPE,stderr=PIPE)
    if p.wait():
        raise Exception(error_message+"\n%s\n%s\n"%(p.stdout.read(),p.stderr.read()))
    return p.stdout.readlines()

def clean_snapshot_dict(d):
    """
    Converts Snapshot tree into tree of form
    {snapshot_name:dict_of_children}
    """
    return {d['name']:clean_snapshot_dict(d) for d in d['children']}

def insert_into_snapshot_dict_with_list(D,l,v):
    """
    Used for building tree of snapshots
    """
    if len(l)==0:
        D['children'].append(v)
    else:
        key = l.pop()
        r = filter(lambda d: d['id']==key, D['children'])
        if not len(r)==0:
            insert_into_snapshot_dict_with_list(r[0],l,v)

def generate_step_hashes(build_steps):
    """
    Generates Hashes for each step in the build process. 
    """

    result = []
    buildcontent = ""
    for step in build_steps:
        verb = step[0]
        if verb == "ADD":
            for root,directories,filenames in os.walk(step[1].split(" ")[0]):
                for filename in sorted(filenames):
                    filename = os.path.join(root,filename)
                    f = open(filename, 'rb')
                    data = f.read().encode('hex')
                    buildcontent+= data
                    f.close()
            buildcontent+=step[1]
        else:
            buildcontent+=step[0]+step[1]

        h = hashlib.sha256(buildcontent).hexdigest()
        result.append((step[0],step[1],h))
    return result

class VirtualMachine:
    """
    Object which allows a single VirtualBox VM to be manipulated. 
    """

    uuid=None
    name=None
    username='vagrant'
    port=None

    def __init__(self,name):
        """
        Initialize the machine by specifying its name. 
        """

        if not check_for_virtualbox():
            raise Exception("VBoxManage cannot be found.")

        vms = list_vms()
        if not name in vms:
            raise Exception("Virtual Machine %s not found."%(name))

        self.uuid = vms[name]
        self.name = name

        self.__configure_ssh()

    def attach(self):
        """
        SSH into box and execute command
        """        
	xshop_path = os.path.dirname(os.path.realpath(clr.__file__))
	key_path = xshop_path+"/defaults/vagrant.key"

        ssh_command = ['ssh',
            '-o','GlobalKnownHostsFile=/dev/null',
            '-o','UserKnownHostsFile=/dev/null',
            '-i',key_path,
            '-o','StrictHostKeyChecking=no',
            '-p',str(self.port),
            '%s@localhost'%(self.username)]

        p = call(ssh_command)

    def ssh(self,command,workdir="~",superuser=False):
        """
        SSH into box and execute command
        """        
	xshop_path = os.path.dirname(os.path.realpath(clr.__file__))
	key_path = xshop_path+"/defaults/vagrant.key"
        ssh_command = ['ssh',
            '-o','GlobalKnownHostsFile=/dev/null',
            '-o','UserKnownHostsFile=/dev/null',
            '-i',key_path,
            '-o','StrictHostKeyChecking=no',
            '-p',str(self.port),
            '%s@localhost'%(self.username),
            "cd %s;%s%s"%(workdir,'sudo ' if superuser else '',command)]
        p = Popen(ssh_command,stdout=PIPE,stderr=PIPE)
        p.wait()
        stdout = p.stdout.read()
        stderr = p.stderr.read()
        return {'return_code':p.returncode,'stdout':stdout,'stderr':stderr}

    def start(self):
        """
        Launch VM and wait for availability. 
        Specify optional Snapshot to use.
        Automatically mounts shared folder.
        """
        logging.info("Starting VM")
        self.__launch()
        self.__mount_shared_folder()

    def change_to_snapshot(self,snapshot):
        """
        Set VM to required snapshot.
        """
        logging.info("Switching To Snapshot")
        vboxmanage(['snapshot',self.uuid,'restore',snapshot],
            "There was an error saving switching to the snapshot.")

    def take_snapshot(self, name):
        """
        Takes a live snapshot, labeling it 
        with the supplied name.
        """
        logging.info("Taking Snapshot")
        self.__unmount_shared_folder()
        vboxmanage(['snapshot',self.uuid,'take',name,'--live'],
            "There was an error saving the snapshot.")
        self.__mount_shared_folder()

    def shutdown(self):
        """
        Shutdown VM, discarding state
        """
        logging.info("Shutting Down VM")
        vboxmanage(['controlvm',self.uuid,'poweroff'],
            "There was an error destroying %s"%(self.name))

    def kernel_reboot(self):
        """
        Gracefully reboots VM, installing new guest additions
        before mounting shared folder. 
        """

        self.ssh('sudo poweroff')

        while self.is_running():
            time.sleep(1)

        self.__launch()
        self.__rebuild_guest_additions()
        self.__mount_shared_folder()

    def __info(self,key=None):
        """
        Returns dictionary of VM info. 
        Optionally specify key or key prefix. 
        Returns None if key not found. 
        Returns dictionary of all matching values to key/prefix. 
        If only one match, returns that value. 
        """
        time.sleep(.1)
        output = vboxmanage(['showvminfo','--machinereadable',self.uuid],
            "There was an error fetching %s's info"%(self.name,))

        info = {k:v for (k,v) in map(lambda line: 
                map(lambda e: e.strip('"\n'), line.split('=')),
                    output)}

        if key:
            try: 
                info = {k:v for (k,v) in info.items() if k in 
                    filter(lambda k: k.startswith(key), info.keys())}
                info = info[info.keys()[0]] if len(info)==1 else info
            except KeyError:
                return None

        return info

    def __launch(self):
        """
        Launch VM and wait for boot. 
        """
        if self.is_running():
            raise Exception("Virtual Machine %s is already running."%(self.name))

        vboxmanage(['startvm','--type','headless',self.uuid],
            "%s failed to start.\n"%(self.name))

        self.__wait_for_boot()

    def is_running(self):
        """
        Returns True if the VM state is 'running'
        """
        return self.__info('VMState')['VMState']=='running'

    def __wait_for_boot(self):
        """
        Pauses until the VM responds to SSH
        """
        logging.info("Waiting for machine to respond")
        self.ssh('whoami')

    def __rebuild_guest_additions(self):
        """
        Instructs the VM to rebuild guest additions. 
        """
        logging.info("Rebuilding Guest Additions")
        self.ssh('/etc/init.d/vboxadd setup',superuser=True)

    def __configure_ssh(self):
        """
        Ensure that port forwarding is configured
        to allow for SSH. If not, selects a suitable
        port and configures it. 
        """
        
        rules = self.__info('Forwarding')
        configure = True

        # Configuration happens too fast after requesting info. 
        time.sleep(.1)

        # Find if any rules match
        # Rules are formatted as
        # ... protocol,host_ip,host_port,guest_ip,guest_port
        if rules:
            if type(rules)==dict:
                for _,rule in rules.items():
                    rule = rule.split(',')
                    if rule[-5]=='tcp' and rule[-1]== '22': 
                        configure = False
                        self.port = rule[-3]
                        break
            else:
                rule = rules.split(',')
                if rule[-5]=='tcp' and rule[-1]== '22':
                    configure = False
                    self.port = rule[-3]

        if configure:
            self.port = '2222'
            vboxmanage(['modifyvm',self.uuid,'--natpf1',"guestssh,tcp,,%s,,22"%(self.port,)],
                "SSH could not be configured.")

        logging.info("SSH Configured, Port %s"%(self.port))

    def __mount_shared_folder(self):
        logging.info("Mounting Shared Folder")
        vboxmanage(['sharedfolder','add',self.uuid,'--transient','--name','vagrant','--hostpath',os.getcwd()],
            "There was a problem sharing the build context with the VM.")
        self.ssh('mkdir -p /vagrant',superuser=True)
        self.ssh('mount -t vboxsf vagrant /vagrant',superuser=True)

    def __unmount_shared_folder(self):
        logging.info("Unmounting Shared Folder")
        self.ssh('umount /vagrant', superuser=True)
        vboxmanage(['sharedfolder','remove',self.uuid,'--transient','--name','vagrant'],
            "There was a problem sharing the build context with the VM.") 

    def snapshots(self):
        """
        Returns a dictionary of snapshots for a given machine. The dictionary 
        is rooted at the 'start' snapshot. If no snapshots or no 'start' snapshot,
        returns None.
        """

        # Read in snapshot data from VBoxManage
        output = vboxmanage(['snapshot',self.uuid,'list','--machinereadable'],
            "There was a problem fetching the snapshots for %s"%(self.name))

        # If there machine has no snapshots, return None
        if any(map(lambda s: "This machine does not have any snapshots" in s, output)):
            return None

        # Filter out Current Snapshot and UUID data
        output = filter(lambda l: not "Current" in l, output)
        output = filter(lambda l: not "UUID" in l, output)

        info = []

        # Parse snapshot info into list of {parent_path:snapshotname}
        for line in output:
            line = map(lambda l: l.strip('"\n'),line.split('='))
            key = line[0]
            value = line[1]
            key = key.split('-')[1:]
            info.append({'k':key,'v':value})

        # Sort list so that children come after parent
        info = list(reversed(sorted(info,cmp=lambda x,y: cmp(len(x['k']), len(y['k'])))))

        # Find root node to initialize dictionary
        s = info.pop()
        result = {'name':s['v'],'children':[]}
        root = result
        
        # Pop off snapshots and place them in the dictionary
        for s in list(reversed(info)): 
            d = {'name':s['v'],'id':s['k'].pop(),'children':[]}
            key = list(reversed(s['k']))
            if s['v']=='start':
                root = d
            insert_into_snapshot_dict_with_list(result,key,d)

        return clean_snapshot_dict(root)

class Provider:
    """
    Exposes methods for manipulating a VirtualBox based virtualized test 
    environment.
    """

    workdir="~"
    config=None
    environment=""
    vm=None


    def __init__(self, config): 
        self.config=config
        self.helper = psupport.Helper(self.config)

    def __run_command(self,command):
        """
        Runs a command within the container during the build process. (As sudo)
        """
        logging.info(self.vm.ssh(command,workdir=self.workdir,superuser=True)['stdout'])

    def __set_environment(self,container):
        """
        Adds test information to the bash environment of a 
        test environment by exporting them in ~/.bashrc
        """
        logging.info("Setting Environment Variables")
        variables = copy.deepcopy(self.config.test_vars)
        variables['container_name'] = container
        
        command = "echo '"
        for var in variables: 
            command += 'export %s="%s"\n'%(var, variables[var])
            self.environment+='export %s="%s";'%(var,variables[var])
        command +="' >> ~/.bashrc"

        self.__run_command(command)

    def __add(self,files):
        [infile,outfile]= files
        extensions = (".tar.gz",".tar.bz2",".tar.xz",".tar")
        infile = str(infile)
        if infile.endswith(extensions):
            sh.run(['tar','-xf',infile])
            for e in extensions:
                infile = infile.replace(e,"")
        self.__run_command("cp -r /vagrant/%s %s"%(infile, outfile))

    def build_environment(self,container):
        """
        Constructs a Vagrant managed virtual machine for specified test 
        participant, based on its Dockerfile. 
        """

        alias = self.config.containers[container]['alias']
    
        logging.info("Building %s:%s"%(container, alias))

        [box, verbs, arguments] = self.helper.read(container, 'xshopvb') 
        build_steps = zip(verbs,arguments)

        self.vm = VirtualMachine(box)
        snapshots = self.vm.snapshots()

        # Copy Context
        self.helper.copycontext(container)
        self.helper.copysource(container)
        self.helper.copypackages(container)
        self.helper.copytestfiles()

        build_steps = generate_step_hashes(build_steps)

        # Check for start snapshot, if not, create
        # TODO

        snapshot = 'start'
        for step in build_steps:
            logging.info(step[0] + " " + step[1])
            # Check if snapshot

            if step[0]=="WORKDIR":
                self.workdir = step[1]


            elif step[2] in snapshots.keys():
                    logging.info("Using Cache --> "+ step[2][0:8])
                    snapshot = step[2]
                    snapshots = snapshots[step[2]]

            else: 
                logging.info("RUNNING")
                if not self.vm.is_running():
                    self.vm.change_to_snapshot(snapshot)
                    self.vm.start()

                # Perform command then take snapshot
                verb = step[0]
                command = step[1]
                if verb=="RUN":
                    self.__run_command(command)
                    self.vm.take_snapshot(step[2])
                    logging.info("\n--> "+step[2][0:8])
                elif verb=="ADD":
                    self.__add(command.split(" "))
                    self.vm.take_snapshot(step[2])
                    logging.info("\n--> "+step[2][0:8])
                elif verb=="KERNEL":
                    self.vm.kernel_reboot()
                    self.vm.take_snapshot(step[2])
                    logging.info("\n --> "+step[2][0:8])
                else:
                    raise exceptions.ProviderError("Command %s not recognize"%(verb,))


        if not self.vm.is_running():
            self.vm.change_to_snapshot(snapshot)
            self.vm.start()

        self.__set_environment(container)

    def run_function(self,container, function):
        """
        Runs a given function in xshop_test.py inside of a specified
        participant in the test environment. Should return 
        {'ret':return_ code, 'stdout':stdout}
        """
        logging.info("Running %s in %s"%(function,container,))
        return self.vm.ssh('python2 -c "import xshop_test;import sys;sys.exit(xshop_test.%s())"'%(function,))

    def attach(self, container):
        logging.info("Attaching environment")   
        self.vm.attach()      
       
    def launch_test_environment(self):
        """
        Launches the full test environment, based on information in 
        test_environment.yml    
        """ 
        logging.info("Launching environment")
        workdir="~"
        logging.info("Copying Test Files")
        self.__add(["test/*","~/"])

    def stop_test_environment(self):
        """ 
        Stops virtual test environment
        """
        logging.info("Stopping environment")
        if self.vm and self.vm.is_running():
            self.vm.shutdown()

    def destroy_environment(self,container):
        """
        Removes virtual environment
        """
        logging.info("Destroying environment")
