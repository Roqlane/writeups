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

To access each of these pages, you need to be loged in. I tried to connect with the default login: nagiosadmin:nagiosadmin as well as a brute force attack, but it didn't work. So, I got stuck and decided to come back to first weird page. I hadn't payed attention the first time I looked at it but the last line seems a little peculiar: it represents elements from the periodic table. When you search it online, you find out that there are indexes linked to this element and remember we first need to find a hidden file so a path. When you write down the value linked to each element, it seems like ascii character values. So I wrote a python code to convert it all.

![image](https://github.com/Roqlane/writeups/assets/78229498/5166c01a-c05f-4a3a-aab3-0ec0c13d8ac6)

We got our path: /PI3T.PNg

![image](https://github.com/Roqlane/writeups/assets/78229498/70797a86-55a1-4b1c-8eeb-943d7b3b449c)

Wtf is that ? Well, first let's try to install it and find the author of this.

![image](https://github.com/Roqlane/writeups/assets/78229498/46c917d1-e6a7-40e4-95f2-887049c309ce)

Artist: Piet Mondrian

Now we have to find out what is this file. The name seems to be piet, I searched it and I discovered it is a programming language. So basically, this image seems to be code and if it is code it can be excuted. For this, it is needed to use npiet as the interpreter. It didn't work as the image was a png format, so I followed the tip and convert it to ppm using gimp. Then the results:

![image](https://github.com/Roqlane/writeups/assets/78229498/18074964-0254-4a3f-bd42-346cb23cbe85)

nagiosadmin%n3p3UQ&9BjLp4$7uhWdYnagiosadmin%n3p3UQ&9BjLp4$7uhWdY

