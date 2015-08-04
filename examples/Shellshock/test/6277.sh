#!/bin/bash
EXITCODE=0

CVE20146277=$((shellshocker="() { x() { _;}; x() { _;} <<a; }" bash -c date 2>/dev/null || echo vulnerable) | grep 'vulnerable' | wc -l)

echo -n "CVE-2014-6277 (segfault): "
if [ $CVE20146277 -gt 0 ]; then
    echo -e "\033[91mVULNERABLE\033[39m"
    EXITCODE=1
else
    echo -e "\033[92mnot vulnerable\033[39m"
fi


exit $EXITCODE
