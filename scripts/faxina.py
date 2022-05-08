import shutil
import os

#Deleta Dados armazenados
try:
    shutil.rmtree('./build/deployments')
except:
    pass

try:
    shutil.rmtree('./dados/paciente')
except:
    pass
try:
    os.mkdir('./dados/paciente')
except:
    pass

try:
    shutil.rmtree('./dados/hosp')
except:
    pass
try:
    os.mkdir('./dados/hosp')
except:
    pass

print('\nDados Sobre Contratos Deletados\n')
exit()