from rolepermissions.roles import AbstractUserRole

class Gerente(AbstractUserRole):
    available_permissions = {'Ver_vendas':True, 'Adicionar_vendas':True}

class Programador(AbstractUserRole):
    available_permissions = {'Ver_banco':True, 'Alterar_codigo':True}