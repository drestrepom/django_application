from django.urls import (
    path,
)
from pokeapi.views import (
    get_pokemon,
)

urlpatterns = [
    # ex: /pokemon/pikachu
    path("pokemon/<str:pokemon_name>/", get_pokemon, name="get_pokemon"),
]
