from django.contrib import admin
from .models import Album, Song, AlbumTracklistItem, MusicManagerUser

admin.site.register(Album)
admin.site.register(Song)
admin.site.register(AlbumTracklistItem)
admin.site.register(MusicManagerUser)
