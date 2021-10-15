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
    create_evolution_chain,
    create_specie,
    get_evolution,
)
from typing import (
    Any,
    Dict,
    Iterator,
    List,
)


class Command(BaseCommand):
    help = "Represent the evolution chain"

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument("evolution_id", type=str)

    def handle(self, *args: Any, **options: Any) -> None:
        evolution_id = options["evolution_id"]
        create_evolution_chain(evolution_id)
        self.stdout.write("The evolution chain has been created")
