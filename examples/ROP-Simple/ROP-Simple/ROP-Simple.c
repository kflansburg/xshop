#include <stdio.h>
#include <unistd.h>
#include <string.h>
int main() {
  char *msg = "Give me your input!\n";
  char buf[0x100];
  write(1, msg, strlen(msg));
  read(0, buf, 0x200);
}
