import os
from brownie import  Paciente,Permissao
from scripts.help import get_account,get_contract
import scripts.ipfs as ipfs
from Crypto.PublicKey import RSA
import Crypto.Cipher.PKCS1_OAEP as PKCS1

class paciente:
    def __init__(self,nome):
        self.nome=nome
        self.conta=get_account(nome)
        self.contratos=()

        #Gera chave RSA
        key=self.importKey()
        self.publickey = key.publickey()

    def addMember(self,nome_hosp):
        contrato=get_contract(self.contratos[0],Paciente)
        try:
            print('conta',self.conta)
            hosp=self.getHosp(nome_hosp)
            contrato.addMember(hosp[0],{"from": self.conta})
            print(nome_hosp,hosp[0],'pode adicionar prontuarios para',self.nome)
        except:
            print(nome_hosp,hosp[0],"já tem permissao para adicionar em",self.nome)

    def removeMember(self,nome_hosp):
        #account=get_account(self.nome)
        contrato=get_contract(self.contratos[0],Paciente)
        hosp=self.getHosp(nome_hosp)
        contrato.removeMember(hosp[0],{"from": self.conta})
        print(nome_hosp,hosp[0],'não pode mais adicionar prontuarios para',self.nome)

    #Retorna a lista de chaves dos Prontuarios 
    def get(self):
        #account=get_account(self.nome)
        contrato=get_contract(self.contratos[0],Paciente)
        r=contrato.get({"from": self.conta})
        
        for x in range(len(r)):
            print(x,' - ',r[x][0])
        return r

    #printa o Prontuario escolhido
    def get_pront(self):
        print("\n---------------------------------------------------")
        print('Dados do Paciente',self.nome)
        r=self.get()
        if len(r)>0:
            x=int(input('Digite um valor valido\n'))
            while x>len(r) or x<0:
                x=int(input('Digite um valor valido\n'))
            info=r[x][0]
            cid=r[x][1]
            arquivo=ipfs.cat(cid)
            return info,arquivo
        else:print('Nenhum prontuario salvo\n')

    def addCombinacao(self,nome_hosp):
        print("\n===================================================")
        print('Escolha o dado que deseja compartilhar com ',nome_hosp)
        r=self.get_pront()
        info=r[0]
        hosp=self.getHosp(nome_hosp)
        #pegar public do arquivo
        #encryptor = PKCS1.new()
        #encrypted=encryptor.encrypt(r[1])
        
        path='./dados/paciente/'+info
        with open(path,'wb') as file:
            file.write(r[1])
        
        cid=ipfs.add(path)
        os.remove(path)
        cid=info+','+cid

        account=get_account(self.nome)
        combinado=str(hosp[0])+str(account)
        contrato=get_contract(self.contratos[1],Permissao)
        perms=contrato.getPronts(combinado,{"from": account})
        
        for perm in perms:
            if info in perm:
                print(nome_hosp,'Já tem permissao de acesso para',info)
                return False
        
        contrato.addPront(combinado,cid,{"from": account})
        print('Permissao adicionada para',nome_hosp,' - ',info)
        
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

    def cria_ficha(self):
        conta=get_account(self.nome)
        if self.contratos!=(): 
            print('\n===========Já tem uma ficha===========')
            #return self.contratos[0],self.contratos[1]
        else:
            print('\n=========== Criando ficha ===========')
            contrato1=Paciente.deploy({"from": conta})
            contrato2=Permissao.deploy({"from": conta})
            print('\n=========== Ficha criada ===========')
            self.contratos=[contrato1,contrato2,[]]
            with open('./dados/contratos/'+self.nome+'.txt','w+') as file:
                file.write(self.contratos[0].address+';'+self.contratos[1].address+';'+str(self.contratos[2]))
            self.atualiza_banco()

    #SC3 -> banco de dados de contas
    def passoInicial(self,nome):
        h=self.getHosp(nome)
        if h:
            print(h)
        else:
            print(nome,'não foi cadastrado')
        #p.contratos=h.cria_ficha(p.nome)

    #pega conta e pk do hospital pelo nome
    def getHosp(self,nome_hosp):
        with open('dados/hospitais.txt','r') as file:
            for hosp in file:
                h=hosp.split(';')
                if h[0]==nome_hosp:
                    return (h[1] ,h[2].replace('\n',''))
        return False

    def get_contratos(self):
        try:
            with open('./dados/contratos/'+self.nome+'.txt','r') as file:
                f=file.readline().split(';')
                aux=[]
                for x in f[2].split(','):
                    aux.append(x)
                self.contratos=[get_contract(f[0],Paciente),get_contract(f[1],Permissao),aux]
                print('=============Contratos já criados=============')  
        except:
            self.cria_ficha()
            self.atualiza_banco()  
            
    def atualiza_banco(self):
        with open('dados/pacientes.txt','r') as file:
            for paciente in file:
                p=paciente.split(';')
                if p[0]==self.nome:
                    return False

        with open('dados/pacientes.txt','a') as file:
            print('escrevendo dados ')
            file.write('\n'+self.nome+';'+str(self.conta)+';'+str(self.publickey.export_key('DER')))
        

#p=paciente('benno',0xc0bcafde29595c4013f5b6e0b70b5e28f8f357c4fab80707279cabf75e508ee5)

p=paciente('benno')
#p.atualiza_banco()

for i in range(1):
    p.get_contratos()
    #p.addMember('hospital_1')
    #p.removeMember('hospital_1')
    p.addCombinacao('hospital_1')