#from paciente import paciente
#from scripts.help import get_account

# Paciente adiciona pront?
#
# Dispositivo
#SC3 -> banco de dados de contas

def visualizar(p):
    #print(p.get_pront())
    p.get_print()
            

""" def consulta(p,h):
    print(p.nome,'foi consultar em ',h.nome)
    #da permissao para adicionar prontuarios
    p.addMember(get_account(h.nome))
    #add combinacao (dados - cid) referente ao prontuario no contrato 1 de um paciente 
    h.add_prontuario(p)

nome=''
p=paciente(nome)
visualizar(p)
 """
if __name__=='__main__':
    passoInicial('hospital_1')
    passoInicial('hospital_5')