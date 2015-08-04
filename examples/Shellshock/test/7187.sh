#!/bin/bash
EXITCODE=0

# CVE-2014-7187
CVE20147187=$(((for x in {1..200}; do echo "for x$x in ; do :"; done; for x in {1..200}; do echo done; done) | bash || echo "vulnerable") | grep 'vulnerable' | wc -l)

echo -n "CVE-2014-7187 (nested loops off by one): "
if [ $CVE20147187 -gt 0 ]; then
    echo -e "\033[91mVULNERABLE\033[39m"
    EXITCODE=1
else
    echo -e "\033[92mnot vulnerable\033[39m"
fi

exit $EXITCODE
