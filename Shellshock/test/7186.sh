#!/bin/bash
EXITCODE=0


# CVE-2014-7186
CVE20147186=$((bash -c 'true <<EOF <<EOF <<EOF <<EOF <<EOF <<EOF <<EOF <<EOF <<EOF <<EOF <<EOF <<EOF <<EOF <<EOF' 2>/dev/null || echo "vulnerable") | grep 'vulnerable' | wc -l)

echo -n "CVE-2014-7186 (redir_stack bug): "
if [ $CVE20147186 -gt 0 ]; then
    echo -e "\033[91mVULNERABLE\033[39m"
    EXITCODE=1
else
    echo -e "\033[92mnot vulnerable\033[39m"
fi

exit $EXITCODE
