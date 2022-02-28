#include <stdio.h>
#include <string.h>
#define MAX 100
int main ()

// dir == / -----> /tmp

{
    char* fs = "/"
    char buf[] = "/tmp";
    int i = 0;
    char *p = strtok (buf, "/");
    char *array[MAX];

    while (p != NULL)
    {
        array[i++] = p;
        p = strtok (NULL, "/");
    }

    for (i = 0; i < 3; ++i) 
        printf("%s\n", array[i]);

    return 0;
}