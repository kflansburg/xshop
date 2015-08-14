#include <stdio.h>
#include <stdlib.h>
#include <string.h>

void ___exit() {
  exit(-1);
}

void evil() {
  ___exit();
  system("/bin/sh");
}

void func(int argc, char** argv) {
  char buf[0x100];
  printf("GIVE ME INPUT\n");
  if (argc < 2) {
    printf("WHY NOT?\n");
    exit(-1);
  }
  strcpy(buf, argv[1]);
}

int main(int argc, char** argv) {
  func(argc, argv);
}
