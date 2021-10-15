from contextlib import (
    suppress,
)
from contextvars import (
    ContextVar,
)
from django.core.management.base import (
    CommandError,
)
import logging
from more_itertools.recipes import (
    pairwise,
)
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
    Iterator,
    List,
    Optional,
)

LOGGER = logging.getLogger("pokeapi")
POKEMONS = ContextVar("POKEMONS", default={})


def extract_evolution_chain(evolves_to: List[Dict[str, Any]]) -> Iterator[str]:
    for evolve in evolves_to:
        yield extract_id_from_uri(evolve["species"]["url"])
        yield from extract_evolution_chain(evolve["evolves_to"])


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


def create_evolution_chain(evolution_chain_id: str) -> None:
    with suppress(Evolution.DoesNotExist):
        evolution = Evolution.objects.get(id=evolution_chain_id)
        LOGGER.info("The evolution chain %s already exits", evolution.name)
        return evolution

    if _evolution := get_evolution(evolution_chain_id):
        evolution = create_evolution(evolution_chain_id)
        evolution_chain = [evolution.specie_id]
        evolution_chain.extend(
            list(extract_evolution_chain(_evolution["chain"]["evolves_to"]))
        )
        for _from, _to in pairwise(evolution_chain):
            create_specie(_from)
            create_specie(_to)
            create_specie(_from, _to)


def create_specie(
    specie_id: str,
    evolves_to_id: Optional[str] = None,
) -> Specie:
    with suppress(Specie.DoesNotExist):
        specie = Specie.objects.get(id=specie_id)
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
        except Specie.DoesNotExist:
            evolves_from = create_specie(evolves_from_id)

    try:
        evolution_chain = Evolution.objects.get(id=evolution_chain_id)
    except Evolution.DoesNotExist:
        evolution_chain = create_evolution_chain(evolution_chain_id)
    specie = Specie(
        id=specie_id,
        evolution_chain=evolution_chain,
        evolves_from=evolves_from,
        evolves_to=evolves_to,
        name=_specie["name"],
    )
    specie.save()
    for _pokemon in _specie["varieties"]:
        pokemon_id = extract_id_from_uri(_pokemon["pokemon"]["url"])
        try:
            pokemon = Pokemon.objects.get(id=pokemon_id)
        except Pokemon.DoesNotExist:
            pokemon = create_pokemon(pokemon_id, specie=specie)
            specie.default_pokemon = pokemon
            specie.save()
    return specie


def get_pokemon(pokemon_id: str) -> Optional[Dict[str, Any]]:
    if _pokemon := POKEMONS.get().get(pokemon_id):
        return _pokemon

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
    with suppress(Pokemon.DoesNotExist):
        pokemon = Pokemon.objects.get(id=pokemon_id)
        LOGGER.info("The pokemon %s already exits", pokemon.name)
        return pokemon
    _pokemon = raw_data or get_pokemon(pokemon_id)
    if not specie and (
        specie_id := extract_id_from_uri(_pokemon["species"]["url"])
    ):
        try:
            specie = Specie.objects.get(id=specie_id)
        except Specie.DoesNotExist:
            specie = create_specie(specie_id)

    # LOGGER.debug("Creating the pokemon %s", _pokemon["name"])
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
