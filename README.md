#XSHOP

## Goals

* Expand CVE metadata
* Develop a toolkit for managing automated testing of libraries and their vulnerabilites. For example:
    * Test a new release of a library against all of its known vulnerabilities
    * Test new vulnerability against all versions of a library to measure impact and detect when the bug was introduced
    * Produce a list of known vulnerbilites that a given system or docker image is suceptible to
    * Experiment to see if compiler flags or wrapper can patch vulnerability
* Develop infrastructure to provide a number of services to facilitate research:
    * Track suceptibility of library versions vs. their known vulnerabilities
    * Keep instructions for compiling old library versions
    * Provide community website for discussion and experimentation

## Template System

### File Templating

To make files easier to author for general cases, a template system is used to populate files with parameters specific to a given build before the build is run. This template is applied to the entire build context of each container. 

For example, the dafault Dockerfile for installing a library that is available in a repository is: 

```
FROM xshop:base_test_image

RUN apt-get -y install {{ library }}={{ version }}-1
```

The templating system will substitute values in for the library and version being built. The template system is implemented using Jinja2. As such, you can use its control flow and looping. As an example in a Dockerfile:

```
RUN apt-get update
{% for pack in deps %}
RUN apt-get -y install {{ pack }}
{% endfor %}
```

Keep in mind that Docker caches consecutive builds up until a new Dockerfile command is found, so try to keep as much of the file the same as possible for different variables, with differing commands placed at the end of the file. 

## Project Layout

A project is intended to describe a particular CVE and test it against a single library. Many different experiments can be run to see how the CVE is affected by different situations. The folder hierarchy is as follows:

```
PROJECT_NAME
|- config.yaml
|- docker-compose.yml
|- packages
|- source
|- containers	
|  |- target
|  |  |- Dockerfile
|  |- attacker
|  |  |- Dockerfile
|- test				
|  |- xshop_test.py	
|- build
```

`config.yaml` stores project constants like library name.

`docker-compose.yml` is used to describe the scenario involved in the exploit including each container and how they are connected. As an example you can set up two communicating containers and perform a MitM attack, a container providing a perticular service and an attacker (used in this Heartbleed example), or a standalone container to check privilege escalation attacks. 

`packages` is where users can place `.deb` packages to quickly install prebuilt versions of the library.

`source` is where users can place source tarballs.

xshop automatically copies the correct source/package version into the build context of the target as long as it follows the proper naming convention:

```
[library]-[version].tar.gz
```
for source. 
```
[library]-[version]
|- [library]_[version]-1_amd64.deb
```
for debian. 

The `containers` directory holds the build context for each player in the test. Say you want additional files to be available to add when building a container, place them in the folder for that container.

The contents of the `test` directory is copied into every container at `/home/`. The hook `run_exploit()` in `xshop_test.py` is where you should perform your exploit. A return code of `2` indicates the exploit succeeded, `0` indicates it failed, and any other nonzero code is considered an error. 


## Usage

### Test Projects

#### Creating a Project
Start a new project ( as an example we will use the Heartbleed bug ):

```
xshop new openssl Heartbleed
```

The general format is `xshop new [target library] [project name]`. The project name doesn't matter and is for personal organization. The target library should be what is used to name the source tarballs. 

In the test folder, I place a python script whose main() function performs the attack and returns 2 for success and 0 for failure. In `xshop\_test.py`: 

```
import os
import heartbleed

def run_exploit():
	if os.environ['CONTAINER_NAME']=='attacker':
		return heartbleed.main()
	return 0
```

Note that each container has an environment variable `CONTAINER_NAME` containing the name assigned to it in the docker-compose.yml file. This allows only executing code on one container and returning 0 for the rest. The results of the test are considered to be the OR of the return codes of the hooks run in each container, so every container not actually performing the exploit should return 0. 

The attacker container should be configured properly because xshop will copy in the test folder and run the exploit hook. We need to set up the target to make sure the library is installed properly. Here we have several options: installing from a repository, installing from a Debian package, installing from source. I will discuss each. 

Note that the responsibilty of properly installing the library is left to the user because it varies wildly by library. The Dockerfile in `containers/target/Dockerfile` contains sane defaults for performing this installation, familiarize yourself with what this does. 

#### Repository
If the library and version to be tested is in a repository that is tracked by the container, it is easy to simply provide the information to apt and install this way. One of the goals of this project is to provide a repository of legacy versions prebuilt for debian:stable, #TODO link to list of libraries. 

Additionally if you wish to provide your own repo, say one produced by an xshop build project, you should modify the target Dockerfile to import your signing public key and add the repository to the sources list. #TODO more here. 

In the Dockerfile, notice that for `install_type==remote`, it simply tries to install from apt and substitute in the version for that test. 

#### Debian
If you have a Debian package, include it in `packages` directory as listed above

At build time, xshop copies this package directory into the build context. In the Dockerfile it copies this into the container and runs dpkg to install and apt to satisfy dependencies mentioned in the package.

#### Source
If you have a source tarball, place it in the target build context. You will most likely have to modify the target Dockerfile to get this to compile, in the case of OpenSSL we must run `./config prefix=/usr` instead of `./Configure` and `make install_sw` intead of `make install`. 

Note that the Dockerfile shows the usage of the template system to select which commands to pass to Docker based on `install_type`. Other variables available to you are `library`, `version`, `build_deps`, `deps`, as well as any independent variable in your test. You can use these variables to splice into commands (for instance the apt-get install used for repository install), or you can use them for additional if statement based control. An example of this would be modifying the commands for compilation for very old versions. 

At build time, xshop copies the tarball into the build context. The default Dockerfile copies this in and then attempts to install it with the default autotools install process. 

#### Running
Next, to run a test. Here is my folder layout:
```
├── build
├── config.yaml
├── containers
│   ├── attacker
│   │   └── Dockerfile
│   └── target
│       ├── Dockerfile
│       ├── server.cert5
│       └── server.key
├── docker-compose.yml
├── packages
│   ├── openssl-1.0.1a
│   │   └── openssl_1.0.1a-1_amd64.deb
│   └── openssl-1.0.1g
│       └── openssl_1.0.1g-1_amd64.deb
├── source
│   ├── openssl-1.0.1a.tar.gz
│   └── openssl-1.0.1g.tar.gz
└── test
    ├── heartbleed.py
    └── xshop_test.py

9 directories, 12 files
```

Note that I have Debian packages for versions `1.0.1a` and `1.0.1g`, as well as source for `1.0.1a` and `1.0.1g`. In the repo, I have `1.0.1a` and `1.0.1g`. For Heartbleed, `1.0.1f` was the last vulnerable version. 

I have also pre-generated certificates for the target server to use and placed them in the target build context, in the target Dockerfile I add these files to make them available to the test server:

```
ADD server.key /home/
ADD server.cert5 /home/
```

In the docker-compose.yml file, I change the run command for the target to:
``` 
/bin/bash -c 'openssl s_server -key server.key -cert server.cert5 -accept 443 -www'
```

This starts a basic ssl server in the target container.

Tests should be run from the root of the project directory. To run the test and install from the repository: 

```
projects/Heartbleed [ xshop test remote 1.0.1a
Running Test: {'version': '1.0.1a'},  Vulnerable
projects/Heartbleed [ xshop test remote 1.0.1g
Running Test: {'version': '1.0.1g'},  Invulnerable
```

Great! The tests confirm other's results with Heartbleed. You might notice that there is very little output. All output, including Docker build output, compilation output, and hook script output is routed to `test.log` in the root of the project folder, which can be monitored with `tail -f test.log`. This is most useful for compilation tests which take some time. In my case, for `1.0.1a`, I find that my script printed out the memory dumped from the vulnerable `1.0.1a` server:

```
.@....SC[...r....+..H...9...
....w.3....f...
...!.9.8.........5...............
.........3.2.....E.D...../...A.................................I.........
...........
...................................#
```

and for `1.0.1g` I find indication that the target server is not vulnerable:

```
Error Receiving Record! timed out
No heartbeat response received, server likely not vulnerable
```

Tests installing from source and Debians are performed similarly:

```
projects/Heartbleed [ xshop test source 1.0.1a
Running Test: {'version': '1.0.1a'},  Vulnerable
projects/Heartbleed [ xshop test debian 1.0.1g
Running Test: {'version': '1.0.1g'},  Invulnerable
```


### API

Another option for running more complivated tests is to use the test module API. 

This exposes two classes, `TestCase` and `Trial`. 

`TestCase` wraps a fixed set of variables and the method to run a test with those variables. 

`Trial` allows you to define multiple independent variables and run all of those tests, returning the results in a multidimensional array. 


Here is an example for Heartbleed, we modify the target Dockerfile to utilize Clang 3.8, allowing us to test some new features.


```
-FROM xshop:base_test_image
+FROM xshop:clang38

...
-RUN make
+RUN make CC=clang CXX=clang++ CFLAG+="{{ cflag }}"

```

This presents two variables now to use: `version` and `cflag`. 

I will now write a script to define a test with the xshop API:

```
#!/usr/bin/python2.7
from xshop import test

var = {'version':
		['1.0.1a','1.0.1g'],
		'cflag':
		['','-fsanitize=address']}

source = 'source'

T = test.Trial(var,source)

T.run()
print T.results()
```

`xshop:clang38` is a default container provided by xshop. (These are locates in `xshop/defaults/contexts`). This pulls the latest version of Clang from the llvm subversion repository, and builds it. This takes a few minutes. To build you can run in a python interpreter:


```
~/xshop [ python                           
Python 2.7.6 (default, Jun 22 2015, 17:58:13) 
[GCC 4.8.2] on linux2
Type "help", "copyright", "credits" or "license" for more information.
>>> from xshop import dockerw
>>> dockerw.build_image('clang38')
>>> 
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
