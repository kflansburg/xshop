#!/bin/bash
EXITCODE=0

# CVE-2014-6278
CVE20146278=$(shellshocker='() { echo vulnerable; }' bash -c shellshocker 2>/dev/null | grep 'vulnerable' | wc -l)

echo -n "CVE-2014-6278 (Florian's patch): "
if [ $CVE20146278 -gt 0 ]; then
    echo -e "\033[91mVULNERABLE\033[39m"
    EXITCODE=1
else
    echo -e "\033[92mnot vulnerable\033[39m"
fi


exit $EXITCODE
