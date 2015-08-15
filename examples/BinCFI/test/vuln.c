#include <stdio.h>
#include <stdlib.h>
#include <string.h>

void func(int argc, char** argv) {
  char buf[0x100];
  if (argc > 1)
    strcpy(buf, argv[1]);
}

int main(int argc, char** argv) {
  func(argc, argv);
}
