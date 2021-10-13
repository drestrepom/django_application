from django.core.management.base import (
    BaseCommand,
    CommandError,
    CommandParser,
)
from more_itertools import (
    pairwise,
)
from pokeapi.models import (
    Evolution,
    Pokemon,
    Specie,
)
import requests  # type: ignore
from typing import (
    Any,
    Dict,
    Iterator,
    List,
    Optional,
)


def get_specie(_id: str) -> Optional[Dict[str, Any]]:
    url = f"https://pokeapi.co/api/v2/pokemon-species/{_id}/"
    response = requests.get(url)
    if response.ok:
        return response.json()

    return None


def extract_id_from_uri(url: str, position: int = -1) -> str:
    return url.split("/")[position - 1]


def extract_evolution_chain(evolves_to: List[Dict[str, Any]]) -> Iterator[str]:
    for evolve in evolves_to:
        yield extract_id_from_uri(evolve["species"]["url"])
        yield from extract_evolution_chain(evolve["evolves_to"])


def create_pokemon(pokemon_id: str, specie: Specie) -> Optional[Pokemon]:
    url = f"https://pokeapi.co/api/v2/pokemon/{pokemon_id}/"
    response = requests.get(url)
    if response.ok:
        result = response.json()
        pokemon = Pokemon(
            name=result["name"],
            id=result["id"],
            specie=specie,
            height=result["height"],
            weight=result["weight"],
        )
        pokemon.save()
        return pokemon
    return None


def create_specie(
    specie_id: str,
    evolves_to_id: Optional[str] = None,
    force_update: Optional[bool] = False,
) -> None:
    evolves_to = None
    if evolves_to_id:
        evolves_to = Specie.objects.get(id=evolves_to_id)

    _specie = get_specie(specie_id)
    if not _specie:
        raise CommandError(f"The specie {specie_id} does not exist")

    evolution_chain_id = extract_id_from_uri(_specie["evolution_chain"]["url"])
    evolves_from = None
    if _from := _specie.get("evolves_from_species", {}):
        evolves_from_id = extract_id_from_uri(_from["url"])
        evolves_from = Specie.objects.get(id=evolves_from_id)

    specie = Specie(
        id=specie_id,
        evolution_chain=Evolution.objects.get(id=evolution_chain_id),
        evolves_from=evolves_from,
        evolves_to=evolves_to,
        name=_specie["name"],
    )
    specie.save(force_update=force_update)
    for _pokemon in _specie["varieties"]:
        pokemon_id = extract_id_from_uri(_pokemon["pokemon"]["url"])
        pokemon = create_pokemon(pokemon_id, specie)
        if _pokemon["is_default"]:
            specie.default_pokemon = pokemon
            specie.save()


def create_evolution(evolution_chain_id: str) -> None:
    url = f"https://pokeapi.co/api/v2/evolution-chain/{evolution_chain_id}/"
    response = requests.get(url)
    if response.ok:
        result = response.json()
        chain = result["chain"]
        specie_id = extract_id_from_uri(chain["species"]["url"])
        Evolution(
            id=evolution_chain_id,
            name=chain["species"]["name"],
            specie_id=specie_id,
        ).save()
        evolution_chain = [specie_id]
        evolution_chain.extend(
            list(extract_evolution_chain(chain["evolves_to"]))
        )
        for _from, _to in pairwise(evolution_chain):
            print(f"{_from}-{_to}")
            create_specie(_from)
            create_specie(_to)
            create_specie(_from, _to, force_update=True)


class Command(BaseCommand):
    help = "Represent the evolution chain"

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument("evolution_id", type=str)

    def handle(self, *args: Any, **options: Any) -> None:
        evolution_id = options["evolution_id"]
        create_evolution(evolution_id)
        self.stdout.write(f"The evolution chain has been created")
