from django.contrib import (
    admin,
)
from pokeapi.models import (
    Evolution,
    Pokemon,
    Specie,
)

# Register your models here.
admin.site.register(Specie)
admin.site.register(Pokemon)
admin.site.register(Evolution)
