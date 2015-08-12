#include <unistd.h>
#include <pthread.h>
#include <stdio.h>

int Global = 0;

void* Thread1(void* args) {
    Global = 42;
    return NULL;
}

int main() {
    pthread_t pt;
    pthread_create(&pt, 0, Thread1, 0);
    Global = 43;
}
