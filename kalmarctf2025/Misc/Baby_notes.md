# Baby CTF

This challenge is based on a real incident that occurred during a CTF competition, which I find quite intriguing. It was discovered that during these competitions, some players created fake teams to manipulate the points allocated to challenges. For instance, imagine there are 100 teams in the competition. An easy challenge solved by 30 teams might be worth 100/1000 points, while a hard challenge solved by only 2 teams might be worth 999/1000 points. By creating fake teams, players could adjust the distribution of points. In this scenario, the easy challenge could end up being worth more than 500 points, while the hard challenge would retain its original value since it is already near the maximum.

This is the premise of Baby CTF. The description mentions that the server uses a flawed algorithm to calculate the points awarded. The goal is to score more than 4000 points by solving only the easy challenges, as the hard ones are deemed impossible to hack. However, after solving the 4 challenges (plus the introductory flag), I didn’t come close to reaching 4000 points.

Here’s where the flaw lies: what if I created 100 more fake teams and then retried submitting the flags? The objective is to make the easy challenges worth as many points as the hard ones.

```python
import requests
from bs4 import BeautifulSoup
import uuid
        
def flood(url):
    """Creates a 100 teams"""
    register_url = url + "/register"
    teams_url = url + "/teams/new"

    for l in range(100):
        try:
            session=requests.Session()
            l = uuid.uuid4()
            
            r1 = session.get(register_url)
            soup = BeautifulSoup(r1.text, 'html.parser')
            input_tag = soup.find('input', attrs={'id': 'nonce', 'type': 'hidden'})
            nonce = input_tag['value']
            register_data = {
                "name": f"{l}",
                "email": f"{l}@gmail.com",
                "password": "meow",
                "nonce": nonce
            }
            reg = session.post(register_url, data=register_data)
            print(register_data)
            print(reg.status_code)
            
            r1 = session.get(teams_url)
            soup = BeautifulSoup(r1.text, 'html.parser')
            input_tag = soup.find('input', attrs={'id': 'nonce', 'type': 'hidden'})
            nonce = input_tag['value']
            team_data = {
                "name": f"{l}",
                "password": f"{l}",
                "nonce": nonce
            }
            reg = session.post(teams_url, data=team_data)
            print(team_data)
            print(reg.status_code)

        except:
            print(f"{l} failed")
            
if __name__ == "__main__":
    url = "https://4c52a8c79c4c79458c1aaafcf1fd90e2-35984.inst1.chal-kalmarc.tf/"
    flood(url)
```

Once the teams were created, the challenges were to be solved. Aside from the introduction flag, 4 challenges were given.

Osint: google reverse image to find the city

Reverse: `strings` on the binary reveals the flag

Forensic: dcode.fr -> braille code

Crypto: 

```python
from Crypto.Util.number import getPrime


with open("flag.txt", "rb") as f:
    flag = f.read()

flag = int.from_bytes(flag, 'big')

e = 65537

p,q,r = [getPrime(512) for _ in "pqr"]

print(f'n1 = {p*q}')
print(f'c1 = {pow(flag, e, p*q)}')
print(f'n2 = {q*r}')
print(f'c2 = {pow(flag, e, q*r)}')
print(f'n3 = {r*p}')
print(f'c3 = {pow(flag, e, r*p)}')
```

```
import math
from Crypto.Util.number import long_to_bytes

n1 = 92045071469462918382808444819504749563961839349096597384482544087908047186245341810642171828493439415203636331750819922984117530107215197072782880474039650967711411408034481971170502798025943494586125686145145275611434604037182033168196599652119558449773401870500131970644786235514317736653798125756404891127
c1 = 83837022114533675382122799116377123399567305874353525217531313052347013266429457590484976944405567987615711918756165213164809141929523845319047846779529628627662566542055574929528850262048285117600900265045865263948170688845876052722196561247534915037323009007843324908963180407442831108561689170430284682827
n2 = 138872353325175299307460237192549876070806082965466021111327520189900415231224864814489473847190673904249096844311163666118481717154197936898625500598207447786178788728989474031735348581801399821380599701957041743964351118199095341359179067904834006929292304447601473687076874217599854120530320878903822568483
c2 = 108277854219556753624555311292632391078510528708411323024976641264748291782337772568140557355433905939549254699367886423180057883496836376992252188314404115061609464533109517754775889103063279929956348746519414221014574988017949824063805698193300538273109123053143777891136649709207700596337731172498156528258
n3 = 96873643524161216047523283610645732806192956944624208819078561364455621631633510067022852244593247313195537163455457833157440906743895116798782534912117642844197952559448815829606193149605373700004399064513744456542191695589096233791113561406431990041145854326610075794048654641871205275800952496149515217589
c3 = 87497536561550257160428999520415606634926951187670727897152089479182062251287235760026406551482417341218358001218344037520058606273067256839313353071151191482530927154606346622780052423032142990543077247694313298271089760031393294084220768215879358822723955182536249471261313038497315002109953940648304272403
e = 65537

r = math.gcd(n2, n3)
p = n3 // r
q = n2 // r

phi = (p-1)*(q-1)
d = pow(e, -1, phi)
meow = pow(c1, d, p*q)

print(long_to_bytes(meow).decode())
```
