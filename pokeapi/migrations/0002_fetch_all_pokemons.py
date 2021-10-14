import aiohttp
import asyncio
from concurrent.futures import (
    ThreadPoolExecutor,
)
from django.db import (
    migrations,
)
import logging
from pokeapi.utils import (
    extract_id_from_uri,
)
from pokeapi.utils.objects import (
    create_pokemon,
)
import requests
from typing import (
    Any,
    Dict,
    Iterable,
    List,
    Optional,
)

logger = logging.getLogger("pokeapi")


async def get_pokemon_data(name: str) -> Optional[Dict[str, Any]]:
    url = f"https://pokeapi.co/api/v2/pokemon/{name}/"
    retries = 0
    while retries < 11:
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(url) as response:
                    if response.ok:
                        return await response.json()
            except aiohttp.client_exceptions.ServerDisconnectedError:
                await asyncio.sleep(0.3)


def get_all_pokemon_ids() -> Iterable[str]:
    url = "https://pokeapi.co/api/v2/pokemon?offset=0&limit=100"
    while True:
        response = requests.get(url)
        if response.ok:
            data = response.json()
            for result in data["results"]:
                yield extract_id_from_uri(result["url"])
            if new_url := data.get("next"):
                url = new_url
            else:
                break
        else:
            break


async def get_all_pokemons_data() -> List[Dict[str, Any]]:
    pokemon_futures = [
        get_pokemon_data(pokemon) for pokemon in get_all_pokemon_ids()
    ]
    return await asyncio.gather(*pokemon_futures)


def main(apps, schema_editor) -> None:
    logger.info("getting all the pokemons")
    all_pokemons = asyncio.run(get_all_pokemons_data())
    logger.info("%s pokemons will be created", len(all_pokemons))
    with ThreadPoolExecutor(max_workers=32) as executor:
        executor.map(
            lambda x: create_pokemon(x["id"], raw_data=x), all_pokemons
        )


class Migration(migrations.Migration):
    dependencies = [("pokeapi", "0001_initial")]
    operations = [migrations.RunPython(main)]
