# Trapped in Plain Sight 2

This one was as easy, looking at the `etc/passwd` file, I found an other user `secretuser` with its password `hunter2` in plaintext. There was also another file at the root `/` names `start.sh`, its content was:

```bash
#!/bin/bash

# cannot setfacl in Dockerfile for some reason
setfacl -m u:$SECRET_USER:r /home/$USER1/flag.txt
unset SECRET_USER
unset USER1

exec /usr/sbin/sshd -D
```

Meaning the the secret user had read permission on the flag.
