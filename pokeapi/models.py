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
    id = models.CharField(primary_key=True, max_length=4)
    evolution_chain = models.ForeignKey(Evolution, on_delete=models.CASCADE)
    evolves_from = models.ForeignKey(
        "self", related_name="from_specie", on_delete=models.CASCADE, null=True
    )
    evolves_to = models.ForeignKey(
        "self", related_name="to_specie", on_delete=models.CASCADE, null=True
    )
    name = models.CharField(max_length=20)
    default_pokemon = models.ForeignKey(
        "pokeapi.Pokemon",
        null=True,
        on_delete=models.CASCADE,
        related_name="default_pokemon",
    )


class Pokemon(models.Model):
    id = models.CharField(primary_key=True, max_length=4)
    name = models.CharField(max_length=20)
    height = models.FloatField()
    weight = models.FloatField()
    specie = models.ForeignKey(Specie, on_delete=models.CASCADE)
    raw_data = models.JSONField(null=True)


class Stat(models.Model):
    stat_id = models.CharField(primary_key=True, max_length=4)
    base_stat = models.IntegerField()
    effort = models.IntegerField()
    name = models.CharField(max_length=20)
    pokemon = models.ForeignKey(Pokemon, on_delete=models.CASCADE)
