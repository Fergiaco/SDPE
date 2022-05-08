import os
from brownie import  Paciente,Permissao
from scripts.help import get_account,get_contract
import scripts.ipfs as ipfs
from Crypto.PublicKey import RSA
import Crypto.Cipher.PKCS1_OAEP as PKCS1

class paciente:
    def __init__(self,nome):
        self.nome=nome
        self.contratos=()
        #Gera chave RSA
        key=self.importKey()
        self.publickey = key.publickey()


    def addMember(self,hosp):
        account=get_account(self.nome)
        contrato=get_contract(self.contratos[0],Paciente)
        try:
            contrato.addMember(hosp,{"from": account})
            print(hosp,'pode adicionar prontuarios para',self.nome)
        except:
            print(hosp,"já tem permissao para adicionar em",self.nome)

    def removeMember(self,hosp):
        account=get_account(self.nome)
        contrato=get_contract(self.contratos[0],Paciente)
        contrato.removeMember(get_account(hosp),{"from": account})
        print(hosp,'não pode mais adicionar prontuarios para',self.nome)

    #Retorna a lista de chaves dos Prontuarios 
    def get(self):
        account=get_account(self.nome)
        contrato=get_contract(self.contratos[0],Paciente)
        r=contrato.get({"from": account})
        for x in range(len(r)):
            print(x,' - ',r[x][0])
        return r

    #printa o Prontuario escolhido
    def get_pront(self):
        r=self.get() 
        info=r[0][0]
        cid=r[0][1]
        encrypted=ipfs.cat(cid)
        decryptor = PKCS1.new(self.importKey())
        decrypted = decryptor.decrypt(encrypted)

        print("\n---------------------------------------------------")
        print('Dados do Paciente',self.nome)
        r=self.get()
        if len(r)>0:
            x=int(input('Digite um valor valido\n'))
            while x>len(r) or x<0:
                x=int(input('Digite um valor valido\n'))
            info=r[x][0]
            cid=r[x][1]
            encrypted=ipfs.cat(cid)
            decryptor = PKCS1.new(self.importKey())
            decrypted = decryptor.decrypt(encrypted)

            #printa prontuario formatado
            #print(decrypted.decode('utf-8').replace('\n',''))
            #retorna desformatado
            return info,decrypted

        else:print('Nenhum prontuario salvo\n')

    def addCombinacao(self,hosp):
        print("\n===================================================")
        print('Escolha o dado que deseja compartilhar com ',hosp.nome)
        r=self.get_pront()
        info=r[0]
        encryptor = PKCS1.new(hosp.publickey)
        encrypted=encryptor.encrypt(r[1])
        path='./dados/paciente/'+info
        file=open(path,'wb')
        file.write(encrypted)
        file.close()

        cid=ipfs.add(path)
        os.remove(path)
        cid=info+','+cid

        account=get_account(self.nome)
        combinado=str(get_account(hosp.nome))+str(account)
        contrato=get_contract(self.contratos[1],Permissao)
        perms=contrato.getPronts(combinado,{"from": account})
        
        for perm in perms:
            if info in perm:
                print(hosp.nome,'Já tem permissao de acesso para',info)
                return False
        
        contrato.addPront(combinado,cid,{"from": account})
        print('Permissao adicionada para',hosp.nome,' - ',info)
        

    def removeCombinacao(self,hosp):
        account=get_account(self.nome)
        contrato=get_contract(self.contratos[1],Permissao)
        combinado=str(get_account(hosp.nome))+str(account)
        r=contrato.getPronts(combinado,{"from": account})
        if len(r)==0:
            print(hosp.nome,'já está sem Permisssao')
            return False

        print("\n===================================================")
        print('Escolha o dado que deseja revogar a permissao de',hosp.nome)
        
        try:
            for i in range(len(r)):
                print(i,'-',r[i])
            
            escolha=int(input())
            pront=r[escolha]
            print('Removendo a permissao de',hosp.nome,'para acessar',pront)
            contrato.removePront(combinado,pront,{"from": account})
            print(hosp.nome,'perdeu o Acesso do',pront)
        except:
            print(hosp.nome,'já está sem Permisssao')

    def importKey(self):
        try:
            file=open('./dados/paciente/'+self.nome,'rb')
            k=file.read()
            k=RSA.import_key(k)
            #print('chave importada ',self.nome)
            return k
        except:
            file=open('./dados/paciente/'+self.nome,'wb')
            key=RSA.generate(2048)
            k=key.exportKey('DER')
            file.write((k))
            print('chave criada ',self.nome)
            return key
            