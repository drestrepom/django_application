from django.core.management.base import (
    BaseCommand,
    CommandParser,
)
from more_itertools import (
    pairwise,
)
from pokeapi.utils import (
    extract_id_from_uri,
)
from pokeapi.utils.objects import (
    create_evolution,
    create_specie,
    get_evolution,
)
from typing import (
    Any,
    Dict,
    Iterator,
    List,
)


def extract_evolution_chain(evolves_to: List[Dict[str, Any]]) -> Iterator[str]:
    for evolve in evolves_to:
        yield extract_id_from_uri(evolve["species"]["url"])
        yield from extract_evolution_chain(evolve["evolves_to"])


def create_evolution_chain(evolution_chain_id: str) -> None:
    if _evolution := get_evolution(evolution_chain_id):
        evolution = create_evolution(evolution_chain_id)
        evolution_chain = [evolution.specie_id]
        evolution_chain.extend(
            list(extract_evolution_chain(_evolution["chain"]["evolves_to"]))
        )
        for _from, _to in pairwise(evolution_chain):
            print(f"{_from}-{_to}")
            create_specie(_from)
            create_specie(_to)
            create_specie(_from, _to)


class Command(BaseCommand):
    help = "Represent the evolution chain"

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument("evolution_id", type=str)

    def handle(self, *args: Any, **options: Any) -> None:
        evolution_id = options["evolution_id"]
        create_evolution_chain(evolution_id)
        self.stdout.write("The evolution chain has been created")
