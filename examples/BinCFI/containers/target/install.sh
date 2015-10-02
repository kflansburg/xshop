pip install bitarray

cd ./cfi
tar -zxvf cfi.tar.gz
tar -zxvf katana.tar.gz
export PROJECT_HOME=/home/cfi/cfi_no_svn
cp -R ${PROJECT_HOME}/rtld_code/bip /home
cp ${PROJECT_HOME}/rtld_code/ld-2.13-segv-quiet-bip-trans.so /home/bip/installdir/lib
ln -sf /home/bip/installdir/lib/ld-2.13-segv-quiet-bip-trans.so /lib/linux-ld.so.4
cp -s /lib32/* /home/bip/installdir/lib

cd /home/cfi/cfi_no_svn/intercept_glibc
make
cd /home/cfi/cfi_no_svn/glookup_policy
make
cd ../
ln -sf ${PROJECT_HOME}/intercept_glibc/ibc.so.6 /lib
ln -sf ${PROJECT_HOME}/glookup_policy/code_no_far_jmp \
                          /lib/glookup_no_far_jmp

cd /home
make
cd /home/cfi/cfi_no_svn/python_rw
./modify_elf.py /home/vuln
