#!/bin/bash
EXITCODE=0

# CVE-2014-6271
CVE20146271=$(env 'x=() { :;}; echo vulnerable' 'BASH_FUNC_x()=() { :;}; echo vulnerable' bash -c "echo test" 2>&1 | grep 'vulnerable' | wc -l)

echo -n "CVE-2014-6271 (original shellshock): "
if [ $CVE20146271 -gt 0 ]; then
    echo -e "\033[91mVULNERABLE\033[39m"
    EXITCODE=1
else
    echo -e "\033[92mnot vulnerable\033[39m"
fi


exit $EXITCODE
