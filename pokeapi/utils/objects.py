from contextlib import (
    suppress,
)
from django.core.exceptions import (
    ObjectDoesNotExist,
)
from django.core.management.base import (
    CommandError,
)
import logging
from pokeapi.models import (
    Evolution,
    Pokemon,
    Specie,
    Stat,
)
from pokeapi.utils import (
    extract_id_from_uri,
)
import requests
from typing import (
    Any,
    Dict,
    Optional,
)

LOGGER = logging.getLogger("pokeapi")


def get_specie(_id: str) -> Optional[Dict[str, Any]]:
    url = f"https://pokeapi.co/api/v2/pokemon-species/{_id}/"
    response = requests.get(url)
    if response.ok:
        return response.json()

    return None


def get_evolution(evolution_id: str) -> Optional[Dict[str, Any]]:
    url = f"https://pokeapi.co/api/v2/evolution-chain/{evolution_id}/"
    response = requests.get(url)
    if response.ok:
        return response.json()
    return None


def create_evolution(evolution_chain_id: str) -> Optional[Evolution]:
    if _evolution := get_evolution(evolution_chain_id):
        chain = _evolution["chain"]
        specie_id = extract_id_from_uri(chain["species"]["url"])
        evolution = Evolution(
            id=evolution_chain_id,
            name=chain["species"]["name"],
            specie_id=specie_id,
        )
        evolution.save()
        return evolution
    return None


def create_specie(
    specie_id: str,
    evolves_to_id: Optional[str] = None,
) -> Specie:
    with suppress(ObjectDoesNotExist):
        specie = Specie.objects.get(id=specie_id)
        LOGGER.info("The specie %s already exits", specie.name)
        return specie

    evolves_to = None
    if evolves_to_id:
        evolves_to = Specie.objects.get(id=evolves_to_id)

    _specie = get_specie(specie_id)
    LOGGER.debug("creating the %s specie", _specie["name"])
    if not _specie:
        raise CommandError(f"The specie {specie_id} does not exist")

    evolution_chain_id = extract_id_from_uri(_specie["evolution_chain"]["url"])
    evolves_from = None
    if _from := _specie.get("evolves_from_species", {}):
        evolves_from_id = extract_id_from_uri(_from["url"])
        try:
            evolves_from = Specie.objects.get(id=evolves_from_id)
        except ObjectDoesNotExist:
            evolves_from = create_specie(evolves_from_id)

    try:
        evolution_chain = Evolution.objects.get(id=evolution_chain_id)
    except ObjectDoesNotExist:
        evolution_chain = create_evolution(evolution_chain_id)
    specie = Specie(
        id=specie_id,
        evolution_chain=evolution_chain,
        evolves_from=evolves_from,
        evolves_to=evolves_to,
        name=_specie["name"],
    )
    specie.save()
    LOGGER.info("the %s specie has been created", _specie["name"])
    for _pokemon in _specie["varieties"]:
        pokemon_id = extract_id_from_uri(_pokemon["pokemon"]["url"])
        try:
            pokemon = Pokemon.objects.get(id=pokemon_id)
        except ObjectDoesNotExist:
            pokemon = create_pokemon(pokemon_id, specie)

        if _pokemon["is_default"]:
            specie.default_pokemon = pokemon
            specie.save()
    return specie


def get_pokemon(pokemon_id: str) -> Optional[Dict[str, Any]]:
    url = f"https://pokeapi.co/api/v2/pokemon/{pokemon_id}/"
    response = requests.get(url)
    if response.ok:
        return response.json()

    return None


def create_pokemon(
    pokemon_id: str,
    raw_data: Optional[Dict[str, Any]] = None,
    specie: Optional[Specie] = None,
) -> Optional[Pokemon]:
    with suppress(ObjectDoesNotExist):
        pokemon = Pokemon.objects.get(id=pokemon_id)
        LOGGER.info("The pokemon %s already exits", pokemon.name)
        return pokemon

    _pokemon = raw_data or get_pokemon(pokemon_id)
    if not specie:
        specie_id = extract_id_from_uri(_pokemon["species"]["url"])
        try:
            specie = Specie.objects.get(id=specie_id)
        except ObjectDoesNotExist:
            specie = create_specie(specie_id)

    LOGGER.debug("Creating the pokemon %s", _pokemon["name"])
    pokemon = Pokemon(
        name=_pokemon["name"],
        id=_pokemon["id"],
        specie=specie,
        height=_pokemon["height"],
        weight=_pokemon["weight"],
        raw_data=_pokemon,
    )
    pokemon.save()
    LOGGER.info("The pokemon %s has been created", _pokemon["name"])
    for _stat in _pokemon["stats"]:
        stat = Stat(
            effort=_stat["effort"],
            base_stat=_stat["base_stat"],
            stat_id=extract_id_from_uri(
                _stat["stat"]["url"],
            ),
            name=_stat["stat"]["name"],
            pokemon=pokemon,
        )
        stat.save()
    return pokemon
