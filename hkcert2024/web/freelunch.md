For this chall, we didn't have a docker-compose to run the challenge so I will just explain briefly what was needed to do. You are redirected to a game where you have to get a score over 300. Of course, it is impossible to to do it manually. When looking at the source code, you can see that the website is sending your score along with a hash to an endpoint. To calculate the hash, it needs the score, the username previously registered and a secret, that is given. It looks something like this:

```js
[...]
let username = "foo";
let secret = "bar";
let score = 301;
let hash = hashScore(username + secret + score);
[...]
//send the hash to the endpoint
```
