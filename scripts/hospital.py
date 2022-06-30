from brownie import Paciente,Permissao
from scripts.help import get_account,get_contract
import scripts.ipfs as ipfs
import random
from Crypto.Cipher import AES
from Crypto.Cipher import PKCS1_OAEP
from Crypto.PublicKey import RSA
import os

class hospital:
    def __init__(self,nome):
        #try:
        #    os.mkdir('./dados/hosp/'+nome)
        #except:
        #    pass

        self.nome=nome
        self.conta=get_account(nome)
        key=self.importKey()
        self.publickey = key.publickey()
        #print(self.publickey)
        
    """ #Hospital cria ficha para o paciente
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
            return (contrato1,contrato2) """

    def geraPront(self,paciente):
        data=str(random.randint(1,28))+'-'+str(random.randint(1,12))+'-'+str(random.randint(1920,2021))
        dados=paciente+'-'+data+'-'+self.nome

        path='./dados/prontuarios/'+dados+'.txt'
        pront=open(path,'w')
        modelo=open('./dados/modelo.txt')
        for linha in modelo:
            linha=linha.replace('\n','')

            if 'Patient Id' in linha:
                linha+=paciente
                #print(linha)
            elif 'Date' in linha:
                linha+=data
                #print(linha)
            elif 'Hospital Id' in linha:
                linha+=self.nome

            pront.write(linha+'\n')

        return(path,dados)
            
    #Hospital adiciona prontuario para contrato paciente se tiver permissao
    def add_prontuario(self,nome_paciente):
        paciente=self.get_pacientes(nome_paciente)
        prontuario=self.geraPront(nome_paciente)
        path=prontuario[0]
        dados=prontuario[1]

        #chave
        #print(paciente[1])
        
        ###Criptografa Prontuario com paciente.publickey
        #with open(path,'rb') as file:
        #    #encryptor=PKCS1_OAEP.new(paciente[1])
        #    encryptor=PKCS1_OAEP.new(RSA.importKey(paciente[1]))
        #    f=file.read()
        #    print(f)
        #    encrypted=encryptor.encrypt(f)
        #print(encrypted)
        #with open(path,'wb') as file:
        #    file.write(encrypted)
        
        #Envia pro ipfs
        cid=ipfs.add(path)
        os.remove(path)
        paciente=self.get_pacientes(nome_paciente)
        if paciente:
            try:
                c=self.importaContratosPaciente(nome_paciente)
                contrato=get_contract(c[0],Paciente)
                contrato.add(dados,cid,{"from": self.conta})
                print('\n=========== Prontuario adicionado ',dados,'===========')
            except:
                print('\nO hospital não tem permissão para adicionar esse prontuário')    
        else:
            print(nome_paciente,'Não ainda não tem uma ficha')

    def get(self,nome_paciente):
        account=get_account(self.nome)
        p=get_account(nome_paciente)
        print("\n---------------------------------------------------")
        print('Cids Disponibilizados pelo Paciente ',nome_paciente,'para o',self.nome,'\n')
        combinado=str(account)+str(p)
        c=self.importaContratosPaciente(nome_paciente)
        contrato=get_contract(c[1],Permissao)
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
            pront=ipfs.cat(cid)
            print('Vizualizando Prontuario -',dado[0])
            print(pront)

            #Descripto
            #encrypted=ipfs.cat(cid)
            #decryptor = PKCS1.new(self.importKey())
            #decrypted = decryptor.decrypt(encrypted)
            #print('Vizualizando Prontuario -',dado[0])
            #print(decrypted.decode('utf-8'))

        except:
            print(self.nome,'Não tem Permissão para acessar dados do paciente',nome_paciente,' \n')
        return r

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

    def get_pacientes(self,nome_paci):
        with open('dados/pacientes.txt','r') as file:
            for hosp in file:
                h=hosp.split(';')
                if h[0]==nome_paci:
                    return (h[1] ,h[2].replace('\n',''))
        return False

    def importaContratosPaciente(self,nome_paciente):
        try:
            with open('./dados/contratos/'+nome_paciente+'.txt','r') as file:
                f=file.readline().split(';')
                aux=[]
                for x in f[2].split(','):
                    aux.append(x)
                return (f[0],f[1],aux)
        except:
            print('=============Paciente não tem contratos=============') 
    
    """     def importaDados(self,hosp):
        print("\n===================================================")
        print(self.nome,"- importando dados de ",hosp.nome)
        file=open('./dados/hosp/'+hosp.nome+'/infos.txt','r')
        for linha in file:
            l=linha.split('; ')
            self.pacientes[l[0]]=[l[1],l[2],l[3].split(',')]
        self.salvaPacientes()
        

    def salvaPacientes(self):
        file=open('./dados/hosp/'+self.nome+'/infos.txt','w')
        for paciente in self.pacientes.keys():
            dados=''
            for dado in self.pacientes[paciente][2]:
                dados+=dado+','
            s=str(paciente)+'; '+str(self.pacientes[paciente][0])+'; '+str(self.pacientes[paciente][1])+'; '+dados[:-1]+'; \n'
            file.write(s)
        file.close()
    """

#def encrypt(raw,key):
#    raw=pad(raw)
#    iv = Random.new().read(AES.block_size)
#    cipher = AES.new(key, AES.MODE_CBC, iv)
#    return base64.b64encode(iv + cipher.encrypt(raw.encode()))

def pad(s):
    bs=AES.block_size
    return s + (bs - len(s) % bs) * chr(bs - len(s) % bs)

h=hospital('hospital_1')
h.add_prontuario('benno')
h.get('benno')