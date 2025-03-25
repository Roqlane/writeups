# Number Champion

This challenge was quite easy, you have an endpoint in which you can launch a match making with another "user". To do so, you have to send your uuid and some locations, then you got a response with the distance from that "user" (based on the provided location), its elo and its name. The goal is to find the user `geopy` and his location. Here's a script to find him.

```python
import requests
elo = 1000
uuid = "093202cc-cb1f-441c-9ccc-c0e2129c3677"
url = "URL" + f"/match?uuid={uuid}&lat=80&lon=10"

while elo < 3000:
    res = requests.post(url)
    text = res.json()
    opponent_elo = int(text.get("elo"), 10)
    if opponent_elo > elo:
        elo = opponent_elo
        uuid = text.get("uuid")
        
print("Found geopy with uuid of", uuid)
```

Once found, you have to find its location. Basically, I just apllied a binary search without writing a script and once I got really near the location I looked it up manually on this site https://www.gps-coordinates.net/.

And after 15minutes of searching, I found it:
Subway, 1059 South High Street, Columbus, OH 43206, United States of America

`utflag{1059-south-high-street-columbus-43206}`
