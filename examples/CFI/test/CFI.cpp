#include <stdio.h>
#include <unistd.h>
#include <string.h>
class Person {
  public:
  virtual void play() {
    printf("I am happy\n");
  }
};

class Student: public Person {
  public:
  virtual void play() {
    printf("I have to study\n");
  }
};

void evil() {
  printf("EVIL\n");
}

int* evil_vftable[2] = {(int*)evil, NULL};

int main() {
  Student* alice = new Student;
  int** ptr = (int**)alice;
  ptr[0] = (int*)evil_vftable; // ovewrite
  alice->play();
}
