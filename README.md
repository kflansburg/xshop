#XSHOP

## General Installation

The install script requires that [PIP](http://pip.readthedocs.org/en/stable/installing/)
is installed. 

XShop requires a virtualization provider, either Docker or Vagrant. Vagrant is
required for testing kernel vulnerabilities, due to limitations of container
virtualization. XShop requires that you can run Docker without `sudo`. 

Then run from the XShop source directory: 
```
./install.sh
```

This installs all Python dependencies, the XShop library, and command line 
utility. 

When using Docker, you will want to build test environments from an image which
includes some software that is not included in typical distribution images 
(such as Python). To build these base images, run:

```
xshop build_image [image_name]
```

* `base_test_image`: installs Python, GCC, Clang, and Make on top of Debian Jessie. 
* `clang38`: builds the latest Clang from source on Debian Jessie. 

Tests using Vagrant can typically begin from a stock distribution box. 


## Project Goals

* Expand CVE metadata
* Develop a toolkit for managing automated testing of libraries and their vulnerabilities. For example:
    * Test a new release of a library against all of its known vulnerabilities
    * Test new vulnerability against all versions of a library to measure impact and detect when the bug was introduced
    * Produce a list of known vulnerabilities that a given system or docker image is susceptible to
    * Experiment to see if compiler flags or wrapper can patch vulnerability
* Develop infrastructure to provide a number of services to facilitate research:
    * Track susceptibility of library versions vs. their known vulnerabilities
    * Keep instructions for compiling old library versions
    * Provide community website for discussion and experimentation

## Template System

### XShopFile

XShop draws inspiration from the Dockerfile format to allow exploit authors to
specify how test environments are built. From Dockerfile, XShop supports four
verbs, `ADD`, `RUN`, `FROM`, `WORKDIR`. Additionally, it supports 
`KERNEL [version]`, which instructs XShop to reboot the environment into the
newly installed kernel version. Finally, authors may specify `FROM_[PROVIDER]`, 
to support multiple providers with different starting image names. 

The most powerful feature of the XShopFile is the ability to support
templating, which allows the author to specifies the ways in which variation
can be introduced into the build process in a controlled manner. Templating
is implemented using Jinja2, and as such control flow and loops are also
supported. 


For example, the dafault XShopFile for installing OpenSSL is:

```
FROM xshop:base_test_image
VAGRANT_FROM ubuntu/precise64

{% if install_type=="debian" %}
    RUN mkdir ~/packages
    ADD {{ library }}-{{ version }} ~/packages/
    RUN dpkg -i ~/packages/*.deb
    RUN apt-get -y install -f

{% elif install_type=='source' %}
    ADD {{ library }}-{{ version }}.tar.gz ~/
    WORKDIR ~/{{ library }}-{{ version }}/
    RUN ./config --prefix=/usr
    RUN make
    RUN make install_sw

{% else %}
    RUN apt-get -y install {{ library }}={{ version }}

{% endif %}
```

Keep in mind that Docker caches consecutive builds up until a new command is 
found, so try to keep as much of the file the same as possible for different 
variables, with differing commands placed at the end of the file. Vagrant
does not support caching, and is much slower in general. 

## Project Layout

A project is intended to describe a particular CVE and test it against a single
library. Many different experiments can be run to see how the CVE is affected 
by different situations. The folder hierarchy is as follows:

```
PROJECT_NAME
|- config.yaml
|- test-environment.yml
|- packages
|- source
|- containers	
|  |- target
|  |  |- XShopFile
|  |- attacker
|  |  |- XShopFile
|- test				
|  |- xshop_test.py
```

A project is created by running `xshop new [library] [folder]`. The folder
name is arbitrary, but the library name is used for manipulating source files
(e.g. [library]-[version].tar.gz). 

### Config.yml

Stores the project configuration. Here is the file used for Heartbleed:

```
constants:
  build-dependencies: []
  dependencies: []
  library: openssl
  install_type: source
  provider: docker
variables:
  version:
    - 1.0.1f
    - 1.0.1g
source:
  - "http://openssl.org/source/old/1.0.0/openssl-1.0.0r.tar.gz"
  - "http://openssl.org/source/old/1.0.1/openssl-{1.0.1a,1.0.1f,1.0.1g}.tar.gz"
public_keys:
  - "F295C759"
  - "0E604491"
notes: |
    Files are signed with F295C759 and
    0E604491, however these keys are
    PGP-2 and GPG will not import.
```

`constants` specify the isolation provider (Vagrant or Docker), library, any
other values that should be present in the build and test environment, and
installation type (source, packages, remote). Source and packages types will
attempt to copy source tarballs from `source/[library]-[version]/` or Debian 
packages from `packages/[library]-[version]/` respectively during build. 

`variables` specifies the basic test to demonstrate the proof of concept (i.e.
`1.0.1f` is vulnerable, `1.0.1g` is not). This is run with `xshop test`. 

`source` specifies URLs where XShop can aquire files needed for the test. XShop
automatically expands tuples ({1.0,2.0,3.0}) into multiple URLs and downloads
each. These files can be downloaded by `xshop pull`. 

`public_keys` allows the author to note which keys the files are signed with. 

`notes` are printed after `xshop pull` downloads the files to notify the user
of any idiosyncrasies. 


### test-environment.yml

Used to describe the scenario involved in the exploit, including each container
and how they are connected. As an example you can set up two communicating 
containers and perform a MitM attack, a container providing a particular 
service and an attacker (used in this Heartbleed example), or a standalone 
container to check privilege escalation attacks. Here is the typical
file for a server-client attack environment such as Heartbleed:

```
attacker:
  build: attacker/
  links:
    - target 
  command: /bin/bash -c "while true; do sleep .1; done"
  environment:
    CONTAINER_NAME: attacker
target:
  build: target/
  environment:
    CONTAINER_NAME: target
  command: /bin/bash -c "while true; do sleep .1; done"
```

### packages

Here users can place packages for the library that should be installed. XShop 
automatically copies all files from `packages/[library]-[version]` into the
build context. From here the user can simply copy and install them during
build. 
 
### source

Much like the packages directory, the user can place source tarballs in this
directory. XShop automatically copies `[library]-[version].tar.gz` into the
build context and the user can install from the XShopFile by copying in the
tarball. Note that Docker/Vagrant automatically decompress the archive. 

### containers

This holds the build context for each container, including XShopFile and any 
other files which may be needed during build. 

### test

This directory holds any files needed during testing. It also holds the 
`xshop_test.py` script for describing the test procedure. 

This script allows the user to run functions within the test environment. The 
user should write the functions to return `2` if there is exploit success and 
`0` if the exploit fails or the function is only a helper function. If any 
function returns `2`, the XShop considers the exploit a success. If any 
function returns non-zero other than `2`, then XShop considers this an error 
and aborts the test. Here is an example script for Heartbleed, the actual
Heartbleed exploit is in the `heartbleed` module and has been modified to
return the needed values:

```
import heartbleed
import subprocess
import os
import time

def run(run_function):
    run_function('target','start_server')
    time.sleep(5)
    run_function('attacker','run_exploit')

def start_server():
    subprocess.Popen(["openssl"
        " s_server"
        " -key"
        " server.key"
        " -cert"
        " server.cert5"
        " -accept"
        " 443"
        " -www"], 
        stdout=subprocess.PIPE,
        stdin=subprocess.PIPE,
        stderr=subprocess.PIPE,
        shell=True)
    return 0

def run_exploit():
    return heartbleed.main()
```

## Testing Kernels

When testing kernels, you must use Vagrant. The installation of the new kernel
proceeds just like any other project. The library name for the project is 
simply set to `linux-image`, and the kernel packages are placed in 
`packages/linux-image-[version]/`. To avoid building your own kernel packages
for the test, you can use Ubuntu boxes, and source kernel packages from 
[Ubuntu Kernel Mainline](http://kernel.ubuntu.com/~kernel-ppa/mainline/). 

For a reliable installation method, it is recommended to place 
`linux-headers-*_amd64.deb`, `linux-headers-*_all.deb`, and 
`linux-image-*_amd64.deb` into the `packages/linux-image-[version]/` folder so
that all are installed together. Upgrading kernels can be tricky because of 
VirtualBox Guest additions. It is recommended to install the Vagrant 
`vagrant-vbguest` plugin to mitigate this. 

It is typically easiest to begin with a box that has a kernel version before 
the version you wish to test, so that when you upgrade it will automatically 
reboot into the newer version. Otherwise, you may need to modify `grub.cfg` 
during the build process. Keep in mind, however, that if the box is
too old, newer kernels will not install smoothly. 

It can be difficult to find boxes for these older versions, although 
[vagrantbox.es](http://www.vagrantbox.es) can be useful. Keep in mind that it 
is difficult to know how these boxes were configured and you may wish to make 
your own. 

**Test boxes must have `python2` symlinked to the Python 2 executable.**

For a better idea of the procedure, take a look at the kernel exploit examples
such as Full Nelson.

## Attaching

To inspect the test environment, it must be able to properly build. The user
can the run `xshop attach [variable1=value1] [variable2=value2] target` to 
launch the environment with the specified variable values and attach a shell
to the specified container. This can be useful for debugging the actual exploit
on particularly slow test environment launches. 

## API

Another option for running more complicated tests is to use the test module API. 

This exposes two classes, `TestCase` and `Trial`. 

`TestCase` wraps a fixed set of variables and the method to run a test with 
those variables. 

`Trial` allows you to define multiple independent variables and run all of 
those tests, returning the results in a multidimensional array. 


Here is an example for Heartbleed, we modify the target XShopFile to utilize 
Clang 3.8, allowing us to test some new features. If you have not already, 
you should build this base image. 


```
-FROM xshop:base_test_image
+FROM xshop:clang38

...
-RUN make
+RUN make CC=clang CXX=clang++ CFLAG+="{{ cflag }}"
```

This presents two hooks now to use within the build process, `version` and `cflag`. 

Now, write a script to define a test with the XShop API:

```
#!/usr/bin/python2.7
from xshop import test

var = {'version':
		['1.0.1a','1.0.1g'],
	'cflag':
		['','-fsanitize=address']}

T = test.Trial(var)

T.run()
print T.results()
```

And run the test. I have formated the results for better legibility:

```
projects/Heartbleed [ ./run
Running Test: {'version': '1.0.1a', 'cflag': ''},  Vulnerable
Running Test: {'version': '1.0.1a', 'cflag': '-fsanitize=address'},  Vulnerable
Running Test: {'version': '1.0.1g', 'cflag': ''},  Invulnerable
Running Test: {'version': '1.0.1g', 'cflag': '-fsanitize=address'},  Invulnerable
[
	[
		{
			'vuln': True, 
			'results': {
				'attacker': {
					'ret': 2, 
					'stdout': '
						attacker
						
						##################################################################
						Connecting to: target:443, 1 times
						
						Sending Client Hello for TLSv1.0
						Received Server Hello for TLSv1.0
	
						WARNING: target:443 returned more data than it should - server is vulnerable!
						Please wait... connection attempt 1 of 1
						##################################################################
			
						.@....SC[...r....+..H...9...
						....w.3....f...
						.".!.9.8.........5..................
						.........3.2.....E.D...../...A.................................I.........
						.4.2..............
						...................................#'
				}, 
				'target': {
					'ret': 0, 
					'stdout': 'target'
				}
			}, 
			'vars': {
				'version': '1.0.1a', 
				'cflag': ''
			}
		}, 
		{
			'vuln': True, 
			'results': {
				'attacker': {
					'ret': 2, 
					'stdout': 'attacker
			
						##################################################################
						Connecting to: target:443, 1 times
						Sending Client Hello for TLSv1.0
						Received Server Hello for TLSv1.0

						WARNING: target:443 returned more data than it should - server is vulnerable!
						Please wait... connection attempt 1 of 1
						##################################################################
			
						.@....SC[...r....+..H...9...
						....w.3....f...
						.".!.9.8.........5..................
						.........3.2.....E.D...../...A.................................I.........
						.4.2..............
						...................................#'
				}, 
				'target': {
					'ret': 0, 
					'stdout': 'target'
				}
			}, 
			'vars': {
				'version': '1.0.1a', 
				'cflag': '-fsanitize=address'
			}
		}
	], 
	[
		{
			'vuln': False, 
			'results': {
				'attacker': {
					'ret': 0, 
					'stdout': 'attacker
			
						##################################################################
						Connecting to: target:443, 1 times
						Sending Client Hello for TLSv1.0
						Received Server Hello for TLSv1.0
					
						Error Receiving Record! timed out
						No heartbeat response received, server likely not vulnerable
						Please wait... connection attempt 1 of 1
						##################################################################'
				}, 
				'target': {
					'ret': 0, 
					'stdout': 'target'
				}
			}, 
			'vars': {
				'version': '1.0.1g', 
				'cflag': ''
			}
		}, 
		{
			'vuln': False, 
			'results': {
				'attacker': {
					'ret': 0, 
					'stdout': 'attacker
			
						##################################################################
						Connecting to: target:443, 1 times
						Sending Client Hello for TLSv1.0
						Received Server Hello for TLSv1.0

						Error Receiving Record! timed out
						No heartbeat response received, server likely not vulnerable
						Please wait... connection attempt 1 of 1
						##################################################################'
				}, 
				'target': {
					'ret': 0, 
					'stdout': 'target'
				}
			}, 
			'vars': {
				'version': '1.0.1g', 
				'cflag': '-fsanitize=address'
			}
		}
	]
]
```

Sadly, this experimental address sanitizer would not have prevented Heartbleed.
