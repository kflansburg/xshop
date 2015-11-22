#!/bin/bash
EXITCODE=0

# CVE-2014-7169
CVE20147169=$((cd /tmp; rm -f /tmp/echo; env X='() { (a)=>\' bash -c "echo echo nonvuln" 2>/dev/null; [[ "$(cat echo 2> /dev/null)" == "nonvuln" ]] && echo "vulnerable" 2> /dev/null) | grep 'vulnerable' | wc -l)

echo -n "CVE-2014-7169 (taviso bug): "
if [ $CVE20147169 -gt 0 ]; then
    echo -e "\033[91mVULNERABLE\033[39m"
    EXITCODE=1
else
    echo -e "\033[92mnot vulnerable\033[39m"
fi

exit $EXITCODE
