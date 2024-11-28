# Use this file for your API viewsets only
# E.g., from rest_framework import ...
from rest_framework import viewsets, permissions
from .models import Album, Song, AlbumTracklistItem, MusicManagerUser
from .serializers import AlbumSerializer, SongSerializer, AlbumTracklistSerializer, MusicManagerUserSerializer

class AlbumViewSet(viewsets.ModelViewSet):
    queryset = Album.objects.all()
    serializer_class = AlbumSerializer

class SongViewSet(viewsets.ModelViewSet):
    queryset = Song.objects.all()
    serializer_class = SongSerializer

class AlbumTracklistViewSet(viewsets.ModelViewSet):
    queryset = AlbumTracklistItem.objects.all()
    serializer_class = AlbumTracklistSerializer

class MusicManagerUserViewSet(viewsets.ModelViewSet):
    queryset = MusicManagerUser.objects.all()
    serializer_class = MusicManagerUserSerializer
