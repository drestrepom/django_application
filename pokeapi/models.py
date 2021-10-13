from __future__ import (
    annotations,
)

from django.db import (
    models,
)


# Create your models here.
class Evolution(models.Model):
    id = models.CharField(primary_key=True, max_length=4)
    name = models.CharField(max_length=20)
    specie_id = models.CharField(max_length=4)


class Specie(models.Model):
    id: models.CharField(primary_key=True, max_length=4)
    evolution_chain = models.ForeignKey(Evolution, on_delete=models.CASCADE)
    evolves_from = models.CharField(null=True, max_length=4)
    evolves_to = models.CharField(null=True, max_length=4)


class Pokemon(models.Model):
    id = models.CharField(primary_key=True, max_length=4)
    name = models.CharField(max_length=20)
    height = models.FloatField()
    weight = models.FloatField()
    specie = models.ForeignKey(Specie, on_delete=models.CASCADE)
