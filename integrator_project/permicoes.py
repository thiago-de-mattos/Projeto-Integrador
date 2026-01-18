from rolepermissions.roles import AbstractUserRole

class Diretoria(AbstractUserRole):
    """Diretoria da ACJOGOS-RJ - Acesso total ao sistema"""
    available_permissions = {
        'editar_todas_empresas': True,
        'editar_todos_perfis': True,
        'editar_todos_projetos': True,
        'gerenciar_permissoes': True,
        'gerar_relatorios': True,
        'ver_dados_completos': True,
    }


class Associado(AbstractUserRole):
    """Empresa ou estúdio filiado à ACJOGOS-RJ"""
    available_permissions = {
        'editar_propria_empresa': True,
        'editar_responsavel_empresa': True,
        'cadastrar_projetos': True,
        'preencher_pesquisa_anual': True,
        'adicionar_links': True,
    }


class Afiliado(AbstractUserRole):
    """Profissional independente vinculado à ACJOGOS-RJ"""
    available_permissions = {
        'editar_proprio_perfil': True,
        'preencher_pesquisa_anual': True,
        'adicionar_links': True,
    }


class Coletivo(AbstractUserRole):
    """Entidades parceiras (universidades, órgãos públicos, incubadoras)"""
    available_permissions = {
        'buscar_empresas': True,
        'gerar_relatorios': True,
        'ver_mapa_empresas': True,
        'exportar_dados_agregados': True,
    }