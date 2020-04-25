from django.contrib import admin

# Register your models here.
from explorer.models import TvChannels, Favourite

admin.site.register(TvChannels)
admin.site.register(Favourite)
