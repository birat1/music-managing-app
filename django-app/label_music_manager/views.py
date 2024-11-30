# Use this file for your templated views only
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import generic
from .models import Album, MusicManagerUser

class AlbumListView(LoginRequiredMixin, generic.ListView):
    model = Album
    context_object_name = 'albums'
    template_name = 'label_music_manager/album_list.html'

    def get_queryset(self):
        user = self.request.user
        music_manager_user = MusicManagerUser.objects.get(user=user)

        if user.is_authenticated and user.has_perm('label_music_manager.Artist'):
            return Album.objects.filter(artist=music_manager_user.display_name) # Artists can only view their own albums
        # Unauthenticated users, viewers, and editors can view all albums.
        return Album.objects.all()