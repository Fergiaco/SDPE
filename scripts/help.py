from brownie import accounts, config
from Crypto import Random
from Crypto import Random
from Crypto.Cipher import AES
import base64


#Retorna versao mais recente do contrato 
def get_contract(address,nome):
    for c in nome:
        if address==c:
            return c
    print('Contrato não existe')

def get_account(conta):
    return accounts.add(config["wallets"][conta])
    
def encrypt(raw,key):
    raw=pad(raw)
    iv = Random.new().read(AES.block_size)
    cipher = AES.new(key, AES.MODE_CBC, iv)
    return base64.b64encode(iv + cipher.encrypt(raw.encode()))

def pad(s):
    bs=AES.block_size
    return s + (bs - len(s) % bs) * chr(bs - len(s) % bs)

def unpad(s):
    return s[:-ord(s[len(s)-1:])]

def decrypt(enc,key):
    enc = base64.b64decode(enc)
    iv = enc[:AES.block_size]
    cipher = AES.new(key, AES.MODE_CBC, iv)
    return unpad(cipher.decrypt(enc[AES.block_size:])).decode('utf-8')
    


