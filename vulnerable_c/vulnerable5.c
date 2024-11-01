#include <stdio.h>
#include <stdlib.h>
#include <pthread.h>
#include <unistd.h>

int balance = 1000;
pthread_mutex_t mutex; 


void *deposit(void *arg) {
    int amount = *((int *)arg);
    // Mutex lock
    pthread_mutex_lock(&mutex);
    int temp = balance;
    temp += amount;
    usleep(1);  
    balance = temp;
    // Mutex unlock
    pthread_mutex_unlock(&mutex);
    return NULL;
}

void *withdraw(void *arg) {
    int amount = *((int *)arg);
    // Mutex lock
    pthread_mutex_lock(&mutex);
    int temp = balance;
    temp -= amount;
    usleep(1); 
    balance = temp;
    // Mutex unlock
    pthread_mutex_unlock(&mutex);
    return NULL;
}

int main() {
    pthread_t t1, t2;
    int deposit_amount = 100;
    int withdraw_amount = 100;

    // mutex 초기화
    pthread_mutex_init(&mutex, NULL);

    pthread_create(&t1, NULL, deposit, &deposit_amount);
    pthread_create(&t2, NULL, withdraw, &withdraw_amount);

    pthread_join(t1, NULL);
    pthread_join(t2, NULL);

    printf("Final balance: %d\n", balance);
    return 0;
}
