from django.db import models

class Skill(models.Model):
    id_user = models.UUIDField()
    skill = models.CharField(max_length=100)
    proeficiencia = models.IntegerField()
    aprendendo = models.BooleanField(default=False)

    
    def __str__(self):
        return f"Usuario: {self.id_user}, Skill: {self.skill}"
