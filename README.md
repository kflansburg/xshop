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
