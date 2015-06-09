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
|  |- test.py			# Provided script with hook functions. 
|  |- exploit.py		# User provided implemention of exploit
```

## Testing

Tests are written using Python's `unittest` module. They are not exhaustive but descibe the main desired functionality. Edge cases will be added as they are discovered. 

Integration testing should ensure that changes don't break the main functionality for typical cases.

To run tests, from the root project directory:

`python -m unittest discover`
