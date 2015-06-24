# glibc

## General Notes

### Build Dependencies

* make
* gcc
* autoconf
* gawk

### Procedure

Must compile in a new build directory. Compile to /usr/local/glibc. Supports parallel build.

```
../glibc/configure --prefix=/usr/local/glibc
make -j16
make install
```

### Running Test:

Run a binary using library:

```
/usr/local/glibc/lib/ld-linux-c86-64.so.2 --library-path /usr/local/glibc/lib [ executable ]
```

## Version Notes

### 2.18

* Correct configure to recognize Make 4.

```
sed -r -i 's/(3..89..)/\1 | 4.*/' {{ library }}-{{ version }}/configure
```

### 2.17

* Correct configure to recognize Make 4, as described in 2.18.

