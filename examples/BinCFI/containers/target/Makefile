TARGET = vuln
SOURCE = $(TARGET).c
HOSTCFLAGS = $(CFLAGS) -fno-stack-protector -m32 -O0
all:
	gcc -o $(TARGET) $(HOSTCFLAGS) $(TARGET).c 

clean:
	@rm -rf $(TARGET)

