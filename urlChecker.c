#include <curl/curl.h>
#include <pthread.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define NUM_THREAD 5
#define WRITE_MAX 5000

// A struct to store the thread arguments
struct thread_data
{
    char *lines; // The file to write the response
    int numUrl;
    FILE *fp;
};

void readFile(char *file, char **lines, int *numUrl)
{
    FILE *fp = fopen(file, "r");
    *lines = NULL;
    *numUrl = 0;

    char *buffer = NULL;
    size_t len = 0; // The length of the buffer

    // Read each line from the file using fgets function
    while (getline(&buffer, &len, fp) != -1)
    {
        // Remove the newline character at the end of the line if present
        buffer = strtok(buffer, "\n");

        // Allocate memory for a new char pointer
        char *line = malloc(strlen(buffer) + 1);

        // Copy the line from the buffer to the new char pointer
        strcpy(line, buffer);

        // Reallocate memory for the array of char pointers
        lines = realloc(lines, (*numUrl + 1) * sizeof(char *));

        // Assign the new char pointer to the array at the current index
        lines[*numUrl] = line;

        // Increment the index by one for the next line
        (*numUrl)++;
    }

    // Close the file
    fclose(fp);
}

// A function to query a URL and parse the JSON response
void *query_and_parse(void *args)
{
    // Cast the args to thread_data struct
    struct thread_data *t = (struct thread_data *)args;
    int num = 0;
    char * data[WRITE_MAX] = {0};
    char * ua = "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Mobile Safari/537.36 Edg/114.0.1823.43";
    // Initialize a curl handle
    CURL *curl = curl_easy_init();
    if (curl)
    {
        // Set the user agent
        curl_easy_setopt(curl, CURLOPT_USERAGENT, ua);
        for (int i = 0; i < t->numUrl; i++)
        {
            // Set the URL to query
            curl_easy_setopt(curl, CURLOPT_URL, t->lines + i);

            // Perform the request and check for errors
            CURLcode res = curl_easy_perform(curl);
            if (res == CURLE_OK)
            {
                long code = 0;
                curl_easy_getinfo(curl, CURLINFO_RESPONSE_CODE, &code);

                if (code == 404)
                {
                    data[num] = t->lines + i;
                    num++;
                }
                else
                {
                    free(t->lines + i);
                }
            }
            else
            {
                free(t->lines + i);
            }

            if (num != 0 && num % WRITE_MAX == 0)
            {
                num = 0;
                for (int j = 0; j < WRITE_MAX; j++)
                {
                    fprintf(t->fp, "%s\n", data[j]);
                    free(data[j]);
                }
                fflush(t->fp);
            }
        }

        // Cleanup the curl handle
        curl_easy_cleanup(curl);
    }
    if (num != 0 && num % WRITE_MAX == 0)
    {
        for (int j = 0; j < num; j++)
        {
            fprintf(t->fp, "%s\n", data[j]);
            free(data[j]);
        }
        fflush(t->fp);
    }
    free(t->lines);
    fclose(t->fp);
    return NULL;
}

int main(int argc, char **argv)
{
    // Check for valid arguments
    if (argc != 6)
    {
        fprintf(stderr, "Usage: %s <file> <file> <file> <file> <file>\n", argv[0]);
        return 1;
    }

    // Create two thread_data structs with arguments
    char * l1 = NULL;
    char * l2 = NULL;
    char * l3 = NULL;
    char * l4 = NULL;
    char * l5 = NULL;
    int s1 = 0;
    int s2 = 0;
    int s3 = 0;
    int s4 = 0;
    int s5 = 0;
    FILE *fp1 = NULL;
    FILE *fp2 = NULL;
    FILE *fp3 = NULL;
    FILE *fp4 = NULL;
    FILE *fp5 = NULL;

    readFile(argv[1], &l1, &s1);
    readFile(argv[2], &l2, &s2);
    readFile(argv[3], &l3, &s3);
    readFile(argv[4], &l4, &s4);
    readFile(argv[5], &l5, &s5);

    fp1 = fopen("out1.txt", "r");
    fp2 = fopen("out2.txt", "r");
    fp3 = fopen("out3.txt", "r");
    fp4 = fopen("out4.txt", "r");
    fp5 = fopen("out5.txt", "r");

    struct thread_data data1 = {l1, s1, fp1};
    struct thread_data data2 = {l2, s2, fp2};
    struct thread_data data3 = {l3, s3, fp3};
    struct thread_data data4 = {l4, s4, fp4};
    struct thread_data data5 = {l5, s5, fp5};

    // Create two threads with query_and_parse function
    pthread_t t1, t2, t3, t4, t5;
    pthread_create(&t1, NULL, query_and_parse, (void *)&data1);
    pthread_create(&t2, NULL, query_and_parse, (void *)&data2);
    pthread_create(&t3, NULL, query_and_parse, (void *)&data3);
    pthread_create(&t4, NULL, query_and_parse, (void *)&data4);
    pthread_create(&t5, NULL, query_and_parse, (void *)&data5);

    // Wait for both threads to finish
    pthread_join(t1, NULL);
    pthread_join(t2, NULL);
    pthread_join(t3, NULL);
    pthread_join(t4, NULL);
    pthread_join(t5, NULL);

    return 0;
}
