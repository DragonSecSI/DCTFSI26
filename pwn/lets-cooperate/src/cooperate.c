#include <setjmp.h>
#include <stdlib.h>
#include <stdio.h>
#include <unistd.h>
#include <stdint.h>
#include <sys/time.h>
#include <fcntl.h>
#include <string.h>

#define STACK_SIZE 2048
enum task_states {
    STOPPED,
    STARTING,
    RUNNING,
    SLEEPING
};

void win(){
	int f = open("flag.txt", O_RDONLY);
	char flag[64];
	read(f, flag, 64);
    printf("%s\n", flag);
    exit(0);
}

struct Task {
    //stores the cpu state
    char stack[STACK_SIZE];
    jmp_buf env;
    void (*func)();
    struct Task *next_task;
    uint8_t state;
    int64_t sleep_until;


    //Pointer to the function that represents the task

    //Pointer to arguments
    void *args;

    //Pointer to next struct
};
jmp_buf scheduler_state;

int64_t currentTimeMillis() {
  struct timeval time;
  gettimeofday(&time, NULL);
  int64_t s1 = (int64_t)(time.tv_sec) * 1000;
  int64_t s2 = (time.tv_usec / 1000);
  return s1 + s2;
}

void task_wrapper(struct Task *this, void *args);

struct Task* new_task(struct Task *head, void *func, void *args){

    struct Task *new_task = malloc(sizeof(struct Task));
    new_task->args = args;
    new_task->func = func;
    new_task->state = STARTING;
    new_task->next_task = head;

    if(!head){
        new_task->next_task = new_task;
        return new_task;
    }

    struct Task *tail = head;
    while(tail->next_task != head){
        tail = tail->next_task;
    }
    tail->next_task = new_task;
}

void start(struct Task *head){
    if(!head){
        printf("Debil head je null\n");
        return;
    }

    struct Task *c = head;
    struct Task *p = head;
    while(c != NULL){

        if(c->state == SLEEPING){
            int64_t currentms = currentTimeMillis();
            if(currentms >= c->sleep_until){
                c->state = RUNNING;
            }else{
                c = c->next_task;
                continue;
            }
        }
        if(c->state == STOPPED){
            //Remove the task from the list
            p->next_task = c->next_task;
            c = c->next_task;
            continue;
        }
        if(setjmp(scheduler_state) != 0){
            //Returned from longjmp
            //Move to the next task
            p = c;
            c = c->next_task;
            continue;
        }
        if(c->state == STARTING){

            c->state = RUNNING;
            //stack_ptr has to point to the end of task->struct, stack grows down!
            register void *stack_ptr = c->stack + sizeof(c->stack);
            asm volatile(
                "mov %[rs], %%rsp \n"
                : [ rs ] "+r" (stack_ptr) ::
            );

            c->func(c, c->args);
            //task_wrapper(c, c->args);
        }else{
            longjmp(c->env, 1);
        }

    }

    exit(0);
}

void yield(struct Task *this){
    if(setjmp(this->env)){
        return;
    }else{
        //Return context to scheduler
        longjmp(scheduler_state, 1);
    }
}

void sleepms(struct Task *this, long msec){
    this->state = SLEEPING;
    this->sleep_until = currentTimeMillis() + msec;
    yield(this);
}

void inline task_wrapper(struct Task *this, void *args){
    this->func(this, args);
    this->state = STOPPED;
    yield(this);
}

// End of scheduler


void command_reader(struct Task *this, void *args){

    char command[16];
    char* command_ptr = command;
    fcntl(STDIN_FILENO, F_SETFL, O_NONBLOCK);

    while(1){

        int r = read(STDIN_FILENO, command_ptr, 1);
        if(r == -1){
            yield(this);
            continue;
        }
        if(r == 0){
            exit(0);
            continue;
        }
        if(*command_ptr == '\n'){
            if(strcmp(command, "dctf{this_is_a_red_herring}\n") == 0){
                printf("Flag defused");
                exit(0);
            }else{
                printf("Unknown command: %s\n", command);
            }
            command_ptr = command;
        }

        command_ptr += r;
        yield(this);
    }
}

void bomb(struct Task *this, void *args){
    while(1){
        static int countdown = 10;
        printf("Bomb: %d\n", countdown);
        fflush(stdout);
        if (countdown <= 0) {
            printf("Boom! \n");
            exit(0);
        }
        countdown--;
        sleepms(this, 1000);
    }
}


int main(int argc, char **argv){

    struct Task *head = new_task(NULL, command_reader , NULL);
    new_task(head, bomb, NULL);

    start(head);
}