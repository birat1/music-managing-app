from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import Album, Song, AlbumTracklistItem, MusicManagerUser

admin.site.register(Album)
admin.site.register(Song)
admin.site.register(AlbumTracklistItem)
admin.site.register(MusicManagerUser)