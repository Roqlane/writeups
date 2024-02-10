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

My guess is that this is a vigenere cipher text. I used this site https://www.guballa.de/vigenere-solver, and secret being bewareTheJabberwock

![image](https://github.com/Roqlane/writeups/assets/78229498/f87b57cf-a29d-44ac-8de3-6600adb45c06)

I think that are creds.

![image](https://github.com/Roqlane/writeups/assets/78229498/389a4ee5-0264-49b9-8a59-69ba282a54e1)

## Privesc

### As jabberwock

When you look at the cron jobs:

![image](https://github.com/Roqlane/writeups/assets/78229498/6a20bd92-939b-42d4-a2af-66131441ef10)

So there is a user who execute our file at reboot

![image](https://github.com/Roqlane/writeups/assets/78229498/a141bc5b-b31a-49cf-8b79-1872f66295fb)

Let's write a reverse shell in this script.

![image](https://github.com/Roqlane/writeups/assets/78229498/bd7a13d6-001a-43f0-b8d6-d9083515d584)

reboot the machine and wait a while:

![image](https://github.com/Roqlane/writeups/assets/78229498/1af20f35-d9a6-4ba7-b3a5-ecb17074fc45)

### As tweedledum

![image](https://github.com/Roqlane/writeups/assets/78229498/97343287-f291-47fa-9d05-d885e378f1b0)

In the new user home directory, we can see this file

![image](https://github.com/Roqlane/writeups/assets/78229498/311e55bb-47ec-4916-88ba-036455fa7d68)

Trying to crack all of this:

![image](https://github.com/Roqlane/writeups/assets/78229498/a02afd6f-dd1b-410a-825e-b444a3d5e942)

You can guess this phrase: maybe one of these is the password.

There is only one of these that I didn't manage to crack:

7468652070617373776f7264206973207a797877767574737271706f6e6d6c6b

After thinking a little, if it is not a hash then it is hex:

![image](https://github.com/Roqlane/writeups/assets/78229498/518f722c-cfe0-42bb-8fdf-17ce38f78500)

### As humptydumpty
