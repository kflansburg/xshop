#include <stdio.h>
#include <string.h>
#include <stdlib.h>
void wrap_exit() {
  exit(-1);
}

void evil() {
  wrap_exit();
  system("/bin/sh");
}

void bof(int argc, char** argv) {
  char buf[0x100];
  strcpy(buf, argv[1]);
}

int main(int argc, char** argv) {
  bof(argc, argv);
}
