# Django Application

## Instructions

- Create a virtual environment

```shell
python -m venv .venv
source .venv/bin/activate
```

- Install dependencies

```shell
pip3 install .
```

### Run migrations

The application has two migrations

- the initial migration that starts the models
- a second migration that extracts the information from all the
  Pokemon and stores it locally, this migration can take a long time


```shell
python manage.py migrate
```

### Commands
The application has a command that allows to extract and store all
the information of an evolution chain

```shell
python migrate.py evolution_chain <chain-id>
```

### Endpoints
the application exposes an endpoint that allows obtaining
information from a pokemon

```shell
curl http://127.0.0.1:8000/pokeapi/pokemon/<pokemon-name>
```
