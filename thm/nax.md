# Nax

https://tryhackme.com/room/nax

## Scan

`nmap -sC -sV 10.10.32.116 -oN scan`

![image](https://github.com/Roqlane/writeups/assets/78229498/aadacffe-1f0a-46e8-8061-c4e9ef7b4092)

## http

The site is a little weird

![image](https://github.com/Roqlane/writeups/assets/78229498/ae00538c-a1e6-47e5-9276-4e07d3f637fc)

`gobuster dir -u "http://10.10.32.116/" --wordlist=/usr/share/wordlists/dirb/common.txt -x .php, .txt`

![image](https://github.com/Roqlane/writeups/assets/78229498/e882a59d-f26f-4b2a-acd2-c0316c443315)

I found another page that seems to be an application.

![image](https://github.com/Roqlane/writeups/assets/78229498/c946500a-908c-4bd6-8b49-5e83d9a3ca57)

If you clikck on the link you are redirected to a login page

![image](https://github.com/Roqlane/writeups/assets/78229498/c7659a2f-b1b5-4743-a32c-b8216fd47431)

I ran another gobuster on the first page

`gobuster dir -u "http://10.10.32.116/nagiosxi" --wordlist=/usr/share/wordlists/dirb/common.txt -x .php, .txt`

![image](https://github.com/Roqlane/writeups/assets/78229498/982586f2-de80-451c-90fb-3ed665cd5cf7)


