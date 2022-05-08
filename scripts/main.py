from scripts.hospital import hospital
from scripts.paciente import paciente
from scripts.help import get_account

def passoInicial(p,h):
    p.contratos=h.cria_ficha(p.nome)
    
def consulta(p,h):
    print(p.nome,'foi consultar em ',h.nome)
    #da permissao para adicionar prontuarios
    p.addMember(get_account(h.nome))
    #add combinacao (dados - cid) referente ao prontuario no contrato 1 de um paciente 
    h.add_prontuario(p)

def visualizacaoPaciente(p):
    #print(p.get_pront())
    p.get_print()
    
def addPermissao(p,h):
    #da permissao
    p.addCombinacao(h)

def removePermissao(p,h):
    #remove permissao 
    p.removeCombinacao(h)

def visualizacaoHospital(p,h):
    #remove permissao 
    h.get(p.nome)
    
    
def main():
    h1=hospital('hosp_1')
    h2=hospital('hosp_2')
    p1=paciente('benno')
    p2=paciente('fernando')
    
    passoInicial(p1,h1)
    passoInicial(p2,h1)
    consulta(p1,h1)

    #Consulta
    #passoInicial(p1,h1)
    #consulta(p1,h1)
    
    #passoInicial(p2,h2)
    #consulta(p1,h1)

    #dados atualizados entre hospitais
    h2.importaDados(h1)
    #h1.importaDados(h2)

    #Da permissao de acesso
    #addPermissao(p1,h1)
    #addPermissao(p1,h2)
    #addPermissao(p2,h2)
    
    #Funciona
    visualizacaoHospital(p1,h1)
    #visualizacaoHospital(p1,h2)
    #visualizacaoHospital(p2,h2)

    #Nao funciona
    visualizacaoHospital(p1,h2)

    #removePermissao(p1,h1)

    #visualizacaoHospital(p1,h1)
    #Nao funciona
    #visualizacaoHospital(p1,h2)