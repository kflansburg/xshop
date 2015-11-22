TARGET=ROP-Simple
SOURCES=$(TARGET).c
HOSTCFLAGS=-fno-stack-protector -m64 $(CFLAGS)
HOSTLDFLAGS=$(LDFLAGS)
ifeq ($(CC),)
	CC = gcc
endif

all:
	$(CC) -o $(TARGET) $(SOURCES) $(HOSTCFLAGS)

clean:
	@rm -rf $(TARGET)
