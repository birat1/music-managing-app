# Use this file for your templated views only
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.db import transaction
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, UpdateView, DeleteView, CreateView
from rest_framework.exceptions import PermissionDenied
from rest_framework.generics import get_object_or_404
from .models import Album, MusicManagerUser, AlbumTracklistItem, Song

class AlbumListView(ListView):
    """
    Displays a list of all albums.
    Artists only see their own albums, while other users can view all albums.
    """
    model = Album
    context_object_name = 'albums'
    template_name = 'label_music_manager/album_list.html'

    def get_queryset(self):
        user = self.request.user

        # Unauthenticated users can view all albums
        if not user.is_authenticated:
            return Album.objects.all()

        # Artists can only view their own albums
        if user.is_authenticated:
            music_manager_user = MusicManagerUser.objects.get(user=user)
            if user.has_perm('label_music_manager.Artist'):
                return Album.objects.filter(artist=music_manager_user.display_name)
        # Viewers and editors can view all albums.
        return Album.objects.all()

    def get_context_data(self, **kwargs):
        """
        Include the display name of the user for template access.
        """
        user = self.request.user
        context = super().get_context_data(**kwargs)

        # Check if the user is authenticated
        if user.is_authenticated:
            music_manager_user = MusicManagerUser.objects.get(user=user)
            context['display_name'] = music_manager_user.display_name

        return context

class AlbumDetailView(DetailView):
    """
    Displays details of a single album.
    Looks up album by its ID and optional slug.
    """
    model = Album
    context_object_name = 'album'
    template_name = 'label_music_manager/album_detail.html'

    def get_object(self, queryset=None):
        """
        Retrieve the album by ID and slug or ID only.
        """
        album_id = self.kwargs.get('id')
        album_slug = self.kwargs.get('slug')

        if album_slug:
            # Look up album by ID and slug
            return get_object_or_404(Album, id=album_id, slug=album_slug)
        # Look up album by ID only (for the /albums/:id format)
        return get_object_or_404(Album, id=album_id)

    def get_context_data(self, **kwargs):
        """
        Add album tracks and display name for template access.
        """
        user = self.request.user
        context = super().get_context_data(**kwargs)

        # Add display name only if the user is authenticated
        if user.is_authenticated:
            music_manager_user = MusicManagerUser.objects.get(user=user)
            context['display_name'] = music_manager_user.display_name

        # Fetch all tracks related to the album through the AlbumTracklistItem model
        album = self.object
        track_items = AlbumTracklistItem.objects.filter(album=album).order_by('position')
        tracks = [item.song for item in track_items]
        context['tracks'] = tracks

        return context

class AlbumEditView(LoginRequiredMixin, UpdateView):
    """
    Handles editing of album details.
    Artists can only edit albums that they are the artist of.
    Editors can edit any album.
    """
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
        """
        Retrieve album object for editing
        """
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
        """
        Retrieves the tracklist of the album with their positions.
        Adds display name for template access and all songs for dropdown.
        """
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
        context['songs'] = Song.objects.all()

        return context

    def form_valid(self, form):
        """
        Handle form submission for album editing.
        Save selected tracks to the album.
        """
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
        """
        Redirect back to album detail page after editing successfully.
        """
        return reverse_lazy('album_detail', kwargs={'id': self.object.id})

class AlbumDeleteView(LoginRequiredMixin, DeleteView):
    """
    Handles deleting an album.
    Only Editors can delete albums.
    """
    model = Album
    context_object_name = 'album'
    template_name = 'label_music_manager/album_confirm_delete.html'

    def get_object(self, queryset=None):
        """
        Retrieve the album for deletion.
        """
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
        """
        Provide confirmation message upon successful deletion.
        """
        messages.success(self.request, 'Album deleted successfully')
        return super().form_valid(form)

    def get_success_url(self):
        """
        Redirect back to album list after successful deletion.
        """
        return reverse_lazy('album_list')

class AlbumCreateView(LoginRequiredMixin, CreateView):
    """
    Handles album creation.
    Only Editors can create albums.
    """
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
        # Only Editors can create albums
        if not request.user.has_perm('label_music_manager.Editor'):
            raise PermissionDenied("You do not have permission to create an album.")
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        """
        Include all songs for dropdown.
        """
        context = super().get_context_data(**kwargs)
        context['songs'] = Song.objects.all()
        context['album'] = self.object if hasattr(self, 'object') else None

        return context

    def form_valid(self, form):
        # Save the album to get an ID
        album = form.save()

        # Add selected tracks to the album
        selected_tracks = self.request.POST.getlist('tracks')
        for track_id in selected_tracks:
            song = Song.objects.get(id=track_id)
            album.tracks.add(song)

        messages.success(self.request, 'Album created successfully.')
        return super().form_valid(form)


    def get_success_url(self):
        """
        Redirect to album list on successful creation.
        """
        return reverse_lazy('album_list')

