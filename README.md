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

## Implementation Notes

* Utilize Docker to quickly construct containers to describe attack scenarios
* Maintain repository of source packages. 
    * Initially Debian, then add RPM support
    * Leverage package manager to satisfy dependencies

## Template System
### File Templating
To make files easier to author for general cases, a template system is used to populate files with parameters specific to a given build before the build is run. 

For example, the dafault Dockerfile for installing a library that is available in a repository is: 

```
FROM xshop:base_test_image

RUN apt-get -y install {{ library }}={{ version }}-1
```

The templating system will substitute values in for the library and version being built. The template system is implemented using Jinja2. As such, you can use its control flow and looping. As an example in a Dockerfile:

```
{% if ARCH == 'armel' %}
FROM xshop:base_image_qemu
{% else %}
FROM xshop:base_image
{% endif %}

{% for pack in deps %}
RUN apt-get -y install {{pack}}
{% endfor %}
```

Each build scenario containers the following variables: `ARCH` (ex. amd64), `DIST` (ex. ubuntu), `RELEASE` (ex. vivid), `VERSION` (ex. 1.0.1-beta1).  
## Project Layout

### Build Project

A build project is intended to assist in developing the configuration information necessary to build packages for many different versions of a library. 

### Test Project

A test project is intended to describe a particular CVE and test it against a library. The folder hierarchy is as follows:

```
PROJECT_NAME
|- docker-compose.yml		# Docker Compose configuration file describing containers to build and launch to make a test environment
|- containers			# Folder containing a subfolder for each container in the test environemnt with Dockerfile and any extra files to copy in
|  |- target
|  |  |- Dockerfile
|  |- attacker
|  |  |- Dockerfile
|- test				# Folder containing a hook script and any supporting code to run the test. This is copied into every container
|  |- xshop_test.py		# Provided script with hook functions. 
|  |- exploit.py		# User provided implemention of exploit
```

## Testing

Tests are written using Python's `unittest` module. They are not exhaustive but descibe the main desired functionality. Edge cases will be added as they are discovered. 

Integration testing should ensure that changes don't break the main functionality for typical cases.

To run tests, from the root project directory:

`python -m unittest discover`

## Usage

### Test Projects

#### Creating a Project
Start a new project ( as an example we will use the Heartbleed bug ):
```
xshop new test openssl Heartbleed
```
The general format is `xshop new [project type] [target library] [project name]`. The project name doesn't matter and is for personal organization. The target library should be what is used to name the source tarballs. 

This creates the default test folder structure mentioned above. The containers folder holds the Docker build context for each participant container in the test environement. The docker-compose.yml describes these containers and any linking between them. The test directory contains a file of hook functions, `xshop_test.py`, which allow you to describe how your code should be executed to perform the test, and in which container. The whole test directory is copied into every container during testing and the hooks run. 

For this example, the docker-compose.yml file is fine because we want to have a the target running a rudimentary OpenSSL server, and the attacker connecting to it to perform the exploit. In the test folder, I place a python script whose main() function performs the attack and returns 1 for success and 0 for failure. In xshop\_test.py: 
```
import os
import heartbleed

def run_exploit():
	if os.environ['CONTAINER_NAME']=='attacker':
		return heartbleed.main()
	return 0
```
Note that each container has an environment variable `CONTAINER_NAME` containing the name assigned to it in the docker-compose.yml file. This allows only executing code on one container and returning 0 for the rest. The results of the test are considered to be the OR of the return codes of the hooks run in each container, so every container not actually performing the exploit should return 0. 

The attacker container should be configured properly, but we need to set up the target to make sure the library is installed properly. Here we have several options: installing from a repository, installing from a Debian package, installing from source. I will discuss each. 

#### Repository
If the library and version to be tested is in a repository that is tracked by the container, it is easy to simply provide the information to APT and install this way. One of the goals of this project is to provide a repository of legacy versions prebuilt for debian:stable, #TODO link to list of libraries. 

Additionally if you wish to provide your own repo, say one produced by an xshop build project, you should modify the target Dockerfile to import your signing public key and add the repository to the sources list. #TODO more here. 

#### Debian
If you have a Debian package, you can simply create a folder `library-version` in the target build context and place the package inside.

#### Source
If you have a source tarball, place it in the target build context. You will most likely have to modify the target Dockerfile to get this to compile, in the case of OpenSSL we must run `./config prefix=/usr` instead of `./Configure` and `make install_sw` intead of `make install`. Note that the Dockerfile shows the usage of the template system to select which commands to pass to Docker. Other variables available to you are `library` and `version`. You can use these variables to splice into commands (for instance the apt-get install used for repository install), or you can use them for additional if statement based control. An example of this would be modifying the commands for compilation for very old versions. 

#### Running
Next, to run a test. Here is my folder layout:
```
├── containers
│   ├── attacker
│   │   └── Dockerfile
│   └── target
│       ├── Dockerfile
│       ├── openssl-1.0.1a
│       │   ├── openssl_1.0.1a-1_amd64.changes
│       │   ├── openssl_1.0.1a-1_amd64.deb
│       │   ├── openssl_1.0.1a-1.debian.tar.xz
│       │   ├── openssl_1.0.1a-1.dsc
│       │   └── openssl_1.0.1a.orig.tar.gz
│       ├── openssl-1.0.1f.tar.gz
│       ├── openssl-1.0.1g
│       │   ├── openssl_1.0.1g-1_amd64.changes
│       │   ├── openssl_1.0.1g-1_amd64.deb
│       │   ├── openssl_1.0.1g-1.debian.tar.xz
│       │   ├── openssl_1.0.1g-1.dsc
│       │   └── openssl_1.0.1g.orig.tar.gz
│       └── openssl-1.0.1g.tar.gz
├── docker-compose.yml
├── test
│   ├── heartbleed.py
│   └── xshop_test.py
```

Note that I have Debian packages for versions `1.0.1a` and `1.0.1g`, as well as source for `1.0.1f` and `1.0.1g`. In the repo, I have `1.0.1a` and `1.0.1g`. For Heartbleed, `1.0.1f` was the last vulnerable version. 

Tests should be run from the root of the project directory. To run the test and install from the repository: 

```
kevin@localhost:~/projects/Heartbleed$ xshop test remote 1.0.1a
True
kevin@localhost:~/projects/Heartbleed$ xshop test remote 1.0.1g
False
```

Great! The tests confirm other's results with Heartbleed. You might notice that there is very little output. All output, including Docker build output, compilation output, and hook script output is routed to `test.log` in the root of the project folder, which can be monitored with `tail -f`. This is most useful for compilation tests which take some time. In my case, for `1.0.1a`, I find that my script printed out the memory dumped from the vulnerable `1.0.1a` server:

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
kevin@localhost:~/projects/Heartbleed$ xshop test source 1.0.1f
True
kevin@localhost:~/projects/Heartbleed$ xshop test debian 1.0.1a
True
```

To experiment with, say, a compiler wrapper or different flags, simply modify the target Dockerfile to install the wrapper or modify the make command to override the flags or compiler variables:

```
RUN make CFLAG="-O3"
```

### Build Projects
