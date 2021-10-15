from django.core.exceptions import (
    ObjectDoesNotExist,
)
from django.http import (
    HttpResponse,
)
from django.http.request import (
    HttpRequest,
)
from django.http.response import (
    JsonResponse,
)
from django.shortcuts import (
    render,
)
from pokeapi.models import (
    Pokemon,
    Specie,
)
from pokeapi.utils.objects import (
    LOGGER,
)


def get_pokemon(request: HttpRequest, pokemon_name: str) -> HttpResponse:
    try:
        response = {}
        pokemon: Pokemon = Pokemon.objects.get(name=pokemon_name)
        pokemon_raw_data = pokemon.raw_data
        pokemon_specie: Specie = pokemon.specie
        response["evolution"] = {}
        LOGGER.info(pokemon_specie)
        if pokemon_specie.evolves_from:
            response["evolution"]["evolves_from"] = {
                "id": pokemon_specie.evolves_from.id,
                "name": pokemon_specie.evolves_from.name,
            }
        if pokemon_specie.evolves_to:
            response["evolution"]["evolves_to"] = {
                "id": pokemon_specie.evolves_to.id,
                "name": pokemon_specie.evolves_to.name,
            }
        response["pokemon"] = pokemon_raw_data
        return JsonResponse(response)
    except ObjectDoesNotExist:
        return JsonResponse(
            {"error": f"the pokemon {pokemon_name} does not exist"}
        )
