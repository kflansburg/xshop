FROM xshop:clang38


ADD Makefile .
ADD ROP-Simple.c . 
RUN make CC=clang CFLAGS="{{ cflags }}" -o /home/ROP-Simple

