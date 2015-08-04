#!/bin/bash
EXITCODE=0

# CVE-2014-////
CVE2014=$(env X=' () { }; echo vulnerable' bash -c 'date' | grep 'vulnerable' | wc -l)

echo -n "CVE-2014-//// (exploit 3 on http://shellshocker.net/): "
if [ $CVE2014 -gt 0 ]; then
    echo -e "\033[91mVULNERABLE\033[39m"
    EXITCODE=1
else
    echo -e "\033[92mnot vulnerable\033[39m"
fi


exit $EXITCODE
