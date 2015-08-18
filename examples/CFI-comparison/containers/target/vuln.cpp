#include <stdio.h>
#include <unistd.h>
#include <string.h>
#include <stdlib.h>

class Person {
  public:
  virtual void play() {
    printf("I am happy\n");
  }
};

__attribute__((used)) void evil() {
  fprintf(stderr, "EVIL\n");
  fflush(stderr);
}

int* fake_vtable[2];

int main(int argc, char** argv) {
  if (argc < 2) return 0;
  Person* alice = new Person;
  strncpy((char*)&fake_vtable[0], argv[1], sizeof(void*));  
  ((void**)alice)[0] = (void*)fake_vtable;
  alice->play();
}
