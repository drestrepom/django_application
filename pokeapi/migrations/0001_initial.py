# Generated by Django 3.2.8 on 2021-10-14 00:44

from django.db import (
    migrations,
    models,
)
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = []  # type: ignore

    operations = [
        migrations.CreateModel(
            name="Evolution",
            fields=[
                (
                    "id",
                    models.CharField(
                        max_length=4, primary_key=True, serialize=False
                    ),
                ),
                ("name", models.CharField(max_length=20)),
                ("specie_id", models.CharField(max_length=4)),
            ],
        ),
        migrations.CreateModel(
            name="Pokemon",
            fields=[
                (
                    "id",
                    models.CharField(
                        max_length=4, primary_key=True, serialize=False
                    ),
                ),
                ("name", models.CharField(max_length=20)),
                ("height", models.FloatField()),
                ("weight", models.FloatField()),
                ("raw_data", models.JSONField(null=True)),
            ],
        ),
        migrations.CreateModel(
            name="Stat",
            fields=[
                (
                    "stat_id",
                    models.CharField(
                        max_length=4, primary_key=True, serialize=False
                    ),
                ),
                ("base_stat", models.IntegerField()),
                ("effort", models.IntegerField()),
                ("name", models.CharField(max_length=20)),
                (
                    "pokemon",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="pokeapi.pokemon",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Specie",
            fields=[
                (
                    "id",
                    models.CharField(
                        max_length=4, primary_key=True, serialize=False
                    ),
                ),
                ("name", models.CharField(max_length=20)),
                (
                    "default_pokemon",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="default_pokemon",
                        to="pokeapi.pokemon",
                    ),
                ),
                (
                    "evolution_chain",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="pokeapi.evolution",
                    ),
                ),
                (
                    "evolves_from",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="from_specie",
                        to="pokeapi.specie",
                    ),
                ),
                (
                    "evolves_to",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="to_specie",
                        to="pokeapi.specie",
                    ),
                ),
            ],
        ),
        migrations.AddField(
            model_name="pokemon",
            name="specie",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                to="pokeapi.specie",
            ),
        ),
    ]
