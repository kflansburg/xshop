// python -c'print"address_of_evil()"'|./a.out
// -> BAD

#include <stdio.h>
#include <unistd.h>
#include <string.h>
#include <stdlib.h>

class Object {
  public:
  virtual void func() {
    fprintf(stderr, "GOOD\n");
  }
};

__attribute__((used)) void evil() {
  fprintf(stderr, "BAD\n");
}

int* fake_vtable[2];

int main(int argc, char** argv) {
  if (argc < 2) return 0;
  Object* obj = new Object;
  strncpy((char*)&fake_vtable[0], argv[1], sizeof(void*));  
  ((void**)obj)[0] = (void*)fake_vtable;
  obj->func();
}
