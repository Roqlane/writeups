import pyotp
secret = "DVDBRAODLCWF7I2ONA4K5LQLUE"

totp = pyotp.TOTP(secret)   
print(totp.now())