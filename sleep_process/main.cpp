#include <stdio.h>
#include <unistd.h>

void the_func()
{
	printf("In the function\n");
	sleep(1);
}

int main()
{
	printf("main\n");
	while(true){
		the_func();
	}

}
