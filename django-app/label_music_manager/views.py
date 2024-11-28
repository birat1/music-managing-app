# Use this file for your templated views only
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import generic
from .models import Album, Song, AlbumTracklistItem, MusicManagerUser

class AlbumListView(LoginRequiredMixin, generic.ListView):
    model = Album

    def get_queryset(self):
        music_manager_user = MusicManagerUser.objects.get(user=self.request.user)

        # If user is an artist, only show their albums
        if music_manager_user.permissions == 'artist':
            return Album.objects.filter(artist=music_manager_user.display_name)
        return Album.objects.all()
