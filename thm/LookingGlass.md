# Looking Glass

https://tryhackme.com/room/lookingglass

## Scan

`nmap -sC -sV 10.10.40.235`

![image](https://github.com/Roqlane/writeups/assets/78229498/db13dd3c-d82b-4f18-8aee-4c210bc8e096)

Lot of ssh services aren't there ? If you try to connect to one of them, you get this result:

`ssh -oHostKeyAlgorithms=+ssh-rsa  10.10.40.235 -p 9001`

![image](https://github.com/Roqlane/writeups/assets/78229498/3d593604-2e03-4c12-b78e-12afe76d234e)

So it is a guess game, after trying several ports, I found the good one:

`ssh -oHostKeyAlgorithms=+ssh-rsa  10.10.40.235 -p 9927`

![image](https://github.com/Roqlane/writeups/assets/78229498/7ad72bb6-8bc7-40d6-9a01-865f294b26c4)

