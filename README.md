# XSHOP

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
    * Initially Debian, then ad RPM support
    * Leverage package manager to satisfy dependencies

## Template System
### File Templating
To make files easier to author for general cases, a template system is used to populate files with parameters specific to a given build before the build is run. 

For example, the dafault Dockerfile for installing a library that is available in a repository is: 

```
FROM xshop:base_test_image

RUN apt-get -y install <%= library %>=<%= version %>-1
```

The templating system will substitute values in for the library and version being built. 

### Template Selection

When looking for which configuration files to use, the folder name with the highest specificity is used ( much like in CSS ). For example, a user is building Debian packages for the OpenSSL library, and has a folder, "debian" configured which successfully packages all versions, except for 0.9.1c. The user can create a new folder, "debian_0.9.1c" to specify rules for that specific version. Folders can have as many qualifiers as you like, separated by underscores. A capital X is used to signify a wildcard, mostly for version numbers. A qualifier that is just a wildcard will be ignored. In the event of a tie in the number of qualifiers which match a particular build, the order of selection is: Architecture > Version > Distribution > Release.

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
