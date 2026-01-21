
from django.db.models.signals import post_save
from django.dispatch import receiver
from rolepermissions.roles import assign_role
from .models import Profile


@receiver(post_save, sender=Profile)
def atribuir_cargo_automatico(sender, instance, created, **kwargs):
    """Quando um Profile é criado, dá o cargo automaticamente
    
    Mapeia tipo_usuario do Profile para a Role correspondente:
    - EMPRESA → Associado
    - PROFISSIONAL → Afiliado
    - PODER_PUBLICO → Coletivo
    - GESTOR → Diretoria (caso tenha no seu Profile)
    """
    
    if created:
        user = instance.user
        tipo = instance.tipo_usuario
        
        if tipo == 'EMPRESA':
            assign_role(user, 'Associado')
        
        elif tipo == 'PROFISSIONAL':
            assign_role(user, 'Afiliado')
        
        elif tipo == 'PODER_PUBLICO':
            assign_role(user, 'Coletivo')
        