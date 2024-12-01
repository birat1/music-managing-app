# Use this file for your templated views only
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, UpdateView, DeleteView, CreateView
from rest_framework.exceptions import PermissionDenied
from rest_framework.generics import get_object_or_404

from .models import Album, MusicManagerUser, AlbumTracklistItem, Song


class AlbumListView(LoginRequiredMixin, ListView):
    model = Album
    context_object_name = 'albums'
    template_name = 'label_music_manager/album_list.html'

    def get_queryset(self):
        user = self.request.user
        music_manager_user = MusicManagerUser.objects.get(user=user)

        # Artists can only view their own albums
        if user.is_authenticated and user.has_perm('label_music_manager.Artist'):
            return Album.objects.filter(artist=music_manager_user.display_name)
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

class AlbumEditView(LoginRequiredMixin, UpdateView):
    model = Album
    fields = [
        'title',
        'cover_image',
        'description',
        'artist',
        'price',
        'format',
        'release_date',
    ]
    template_name = 'label_music_manager/album_edit.html'
    context_object_name = 'album'

    def get_object(self, queryset=None):
        album_id = self.kwargs.get('id')
        album = get_object_or_404(Album, id=album_id)

        user = self.request.user
        music_manager_user = MusicManagerUser.objects.get(user=user)

        # Check if the user has the 'Editor' permission
        if user.has_perm('label_music_manager.Editor'):
            return album

        # Check if the user is the artist of the album
        if user.has_perm('label_music_manager.Artist') and album.artist == music_manager_user.display_name:
            return album

        # If neither condition is met, raise a PermissionDenied error
        raise PermissionDenied("You do not have permission to edit this album.")

    def get_context_data(self, **kwargs):
        user = self.request.user
        context = super().get_context_data(**kwargs)

        music_manager_user = MusicManagerUser.objects.get(user=user)
        context['display_name'] = music_manager_user.display_name

        # Fetch all tracks related to the album through the AlbumTracklistItem model
        album = self.object
        track_items = AlbumTracklistItem.objects.filter(album=album).order_by('position')
        # Format tracks as Position: Track Name and join them with newlines
        tracks_string = "\n".join([f"{item.position}: {item.song.title}" for item in track_items])
        context['tracks'] = tracks_string

        # Pass all available songs to the template for the dropdown
        context['songs'] = Song.objects.all()

        return context

    def form_valid(self, form):
        # Handle saving the selected tracks
        album = form.save(commit=False)
        selected_tracks = self.request.POST.getlist('tracks')

        # Clear existing tracks and add the selected ones
        album.tracks.clear()
        for track_id in selected_tracks:
            song = Song.objects.get(id=track_id)
            album.tracks.add(song)

        album.save()
        messages.success(self.request, 'Album updated successfully.')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('album_detail', kwargs={'id': self.object.id})

class AlbumDeleteView(LoginRequiredMixin, DeleteView):
    model = Album
    context_object_name = 'album'
    template_name = 'label_music_manager/album_confirm_delete.html'

    def get_object(self, queryset=None):
        album_id = self.kwargs.get('id')
        album = get_object_or_404(Album, id=album_id)

        user = self.request.user
        music_manager_user = MusicManagerUser.objects.get(user=user)

        # Editors are able to delete albums
        if user.has_perm('label_music_manager.Editor'):
            return album
        # Artists cannot delete their own albums
        if user.has_perm('label_music_manager.Artist') and album.artist == music_manager_user.display_name:
            raise PermissionDenied("Artists cannot delete their own albums.")
        # If not editor, then you cannot delete albums
        raise PermissionDenied("You do not have permission to delete this album.")

    def form_valid(self, form):
        messages.success(self.request, 'Album deleted successfully')
        return super().form_valid(form)

    def get_success_url(self):
        # Redirect to the album list after a successful delete
        return reverse_lazy('album_list')

class AlbumCreateView(LoginRequiredMixin, CreateView):
    model = Album
    fields = [
        'title',
        'cover_image',
        'description',
        'artist',
        'price',
        'format',
        'release_date',
    ]
    template_name = 'label_music_manager/album_edit.html'
    context_object_name = 'album'

    def dispatch(self, request, *args, **kwargs):
        if not request.user.has_perm('label_music_manager.Editor'):
            raise PermissionDenied("You do not have permission to create an album.")
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['songs'] = Song.objects.all()
        # Ensure 'album' key is included to mimic the existing instance
        context['album'] = self.object if hasattr(self, 'object') else None
        return context

    def form_valid(self, form):
        messages.success(self.request, 'Album created successfully.')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('album_detail', kwargs={'id': self.object.id})

