import Crypto.Cipher.PKCS1_OAEP as PKCS1
from brownie import Paciente,Permissao
from scripts.help import get_account,get_contract
import scripts.ipfs as ipfs
from scripts.paciente import paciente
import scripts.ipfs as ipfs
import random
from Crypto import Random
from Crypto.Cipher import AES
from Crypto.PublicKey import RSA
import base64
import os

class hospital:
    def __init__(self,nome):
        try:
            os.mkdir('./dados/hosp/'+nome)
        except:
            pass

        self.nome=nome
        self.pacientes=self.importaPacientes()
        key=self.importKey()
        self.publickey = key.publickey()
        
    #Hospital cria ficha para o paciente
    def cria_ficha(self,paciente):
        p=get_account(paciente)
        if p in self.pacientes: 
            print('\n===========Paciente ',paciente,' já tem uma ficha===========')
            return self.pacientes[p][0],self.pacientes[p][1]
        else:
            account=get_account(self.nome)
            print('\n=========== Criando ficha para o paciente ',paciente,'===========')
            contrato1=Paciente.deploy(p,{"from": account})
            contrato2=Permissao.deploy(p,{"from": account})
            print('\n=========== Ficha criada para o paciente ',paciente,'===========')
            self.pacientes[p]=[contrato1,contrato2,[]]
            self.salvaPacientes()
            return (contrato1,contrato2)

    def geraPront(self,paciente):
        data=str(random.randint(1,28))+'-'+str(random.randint(1,12))+'-'+str(random.randint(1920,2021))
        dados=paciente+'-'+data+'-'+self.nome

        path='./dados/hosp/'+self.nome+'/'+dados+'.txt'
        print(path)

        
        pront=open(path,'w')
        modelo=open('./dados/modelo.txt')
        for linha in modelo:
            linha=linha.replace('\n','')

            if 'Patient Id' in linha:
                linha+=paciente
                print(linha)
            elif 'Date' in linha:
                linha+=data
                print(linha)
            elif 'Hospital Id' in linha:
                linha+=self.nome

            pront.write(linha+'\n')

        return(path,dados)
            
    #Hospital adiciona prontuario para contrato paciente se tiver permissao
    def add_prontuario(self,paciente):
        account=get_account(self.nome)
        p=get_account(paciente.nome)

        prontuario=self.geraPront(paciente.nome)
        path=prontuario[0]
        dados=prontuario[1]

        file=open(path,'rb')
        encryptor=PKCS1.new(paciente.publickey)
        encrypted=encryptor.encrypt(file.read())
        
        ##Criptografa Prontuario com paciente.publickey
        file=open(path,'wb')
        file.write(encrypted)
        file.close()

        #Envia pro ipfs
        cid=ipfs.add(path)
        os.remove(path)

        if p not in self.pacientes:
            print(paciente.nome,'Não ainda não tem uma ficha no',self.nome)
        elif dados not in self.pacientes[p][2]:
            try:
                contrato=get_contract(self.pacientes[p][0],Paciente)
                contrato.add(dados,cid,{"from": account})
                print('\n=========== Prontuario adicionado ',dados,'===========')
                self.pacientes[p][2].append(dados)
                self.salvaPacientes()
                #return contrato
            except:
                print('\nO hospital não tem permissão para adicionar esse prontuário')
        else:
            print(self.nome,'já adicionou esse prontuário para',paciente.nome)

    def get(self,paciente):
        account=get_account(self.nome)
        p=get_account(paciente)
        print("\n---------------------------------------------------")
        print('Cids Disponibilizados pelo Paciente ',paciente,'para o',self.nome,'\n')
        combinado=str(account)+str(p)
        contrato=get_contract(self.pacientes[p][1],Permissao)
        try:
            r=contrato.get(combinado,{"from": account})
            if len(r)==0:
                print('Não tem permissao')
                return False
            
            print('Qual Prontuario deseja Descriptografar?')
            for x in range(len(r)):
                dado=r[x].split(',')
                print(x,'-',dado[0],'\n')
            escolha=int(input())
            
            dado=r[escolha].split(',')
            cid=dado[1]
            encrypted=ipfs.cat(cid)
            decryptor = PKCS1.new(self.importKey())
            decrypted = decryptor.decrypt(encrypted)
            print('Vizualizando Prontuario -',dado[0])
            print(decrypted.decode('utf-8'))

        except:
            print(self.nome,'Não tem Permissão para acessar dados do paciente',paciente,' \n')
        return r

    def importaDados(self,hosp):
        print("\n===================================================")
        print(self.nome,"- importando dados de ",hosp.nome)
        file=open('./dados/hosp/'+hosp.nome+'/infos.txt','r')
        for linha in file:
            l=linha.split('; ')
            self.pacientes[l[0]]=[l[1],l[2],l[3].split(',')]
        self.salvaPacientes()
        
    def importaPacientes(self):
        try:
            file=open('./dados/hosp/'+self.nome+'/infos.txt','x')
        except:
            pass

        pacientes={}
        file=open('./dados/hosp/'+self.nome+'/infos.txt','r')
        for linha in file:
            l=linha.split('; ')
            pacientes[l[0]]=[l[1],l[2],l[3].split(',')]
        return pacientes

    def salvaPacientes(self):
        file=open('./dados/hosp/'+self.nome+'/infos.txt','w')
        for paciente in self.pacientes.keys():
            dados=''
            for dado in self.pacientes[paciente][2]:
                dados+=dado+','
            s=str(paciente)+'; '+str(self.pacientes[paciente][0])+'; '+str(self.pacientes[paciente][1])+'; '+dados[:-1]+'; \n'
            file.write(s)
        file.close()

    def importKey(self):
        try:
            file=open('./dados/hosp/'+self.nome+'/key','rb')
            k=file.read()
            k=RSA.import_key(k)
            #print('chave importada ',self.nome)
            return k
    
        except:
            file=open('./dados/hosp/'+self.nome+'/key','wb')
            key=RSA.generate(2048)
            k=key.exportKey('DER')
            file.write(k)
            #file.close()
            print('chave criada ',self.nome)
            return key
            
#def encrypt(raw,key):
#    raw=pad(raw)
#    iv = Random.new().read(AES.block_size)
#    cipher = AES.new(key, AES.MODE_CBC, iv)
#    return base64.b64encode(iv + cipher.encrypt(raw.encode()))

def pad(s):
    bs=AES.block_size
    return s + (bs - len(s) % bs) * chr(bs - len(s) % bs)