# Use this file for your templated views only
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, UpdateView
from rest_framework.exceptions import PermissionDenied
from rest_framework.generics import get_object_or_404

from .models import Album, MusicManagerUser, AlbumTracklistItem


class AlbumListView(LoginRequiredMixin, ListView):
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

    def get_context_data(self, **kwargs):
        user = self.request.user
        context = super().get_context_data(**kwargs)

        music_manager_user = MusicManagerUser.objects.get(user=user)
        context['display_name'] = music_manager_user.display_name

        return context

class AlbumDetailView(LoginRequiredMixin, DetailView):
    model = Album
    context_object_name = 'album'
    template_name = 'label_music_manager/album_detail.html'

    def get_object(self, queryset=None):
        album_id = self.kwargs.get('id')
        album_slug = self.kwargs.get('slug')

        if album_slug:
            # Look up album by ID and slug
            return get_object_or_404(Album, id=album_id, slug=album_slug)
        # Look up album by ID only (for the /albums/:id format)
        return get_object_or_404(Album, id=album_id)

    def get_context_data(self, **kwargs):
        user = self.request.user
        context = super().get_context_data(**kwargs)

        music_manager_user = MusicManagerUser.objects.get(user=user)
        context['display_name'] = music_manager_user.display_name

        # Fetch all tracks related to the album through the AlbumTracklistItem model
        album = self.object
        track_items = AlbumTracklistItem.objects.filter(album=album).order_by('position')
        tracks = [item.song for item in track_items]
        context['tracks'] = tracks

        return context