# Write your serializers here
from rest_framework import serializers
from django.urls import reverse
from .models import Album, Song, AlbumTracklistItem, MusicManagerUser


class SongSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='songs-detail')

    class Meta:
        model = Song
        fields = ['id', 'url', 'title', 'length']



class AlbumSerializer(serializers.ModelSerializer):
    tracks = SongSerializer(many=True, read_only=True)
    short_description = serializers.SerializerMethodField()
    release_year = serializers.SerializerMethodField()
    total_playtime = serializers.SerializerMethodField()
    url = serializers.HyperlinkedIdentityField(view_name='albums-detail')

    class Meta:
        model = Album
        fields = [
            'id',
            'total_playtime',
            'short_description',
            'release_year',
            'tracks',
            'url',
            'cover_image',
            'title',
            'description',
            'artist',
            'price',
            'format',
            'release_date',
            'slug',
        ]

    def get_short_description(self, obj):
        if len(obj.description) > 255:
            return obj.description[:255] + '...'
        return obj.description

    def get_release_year(self, obj):
        return obj.release_date.year

    def get_total_playtime(self, obj):
        return sum(song.length for song in obj.tracks.all())


class AlbumTracklistSerializer(serializers.ModelSerializer):
    class Meta:
        model = AlbumTracklistItem
        fields = ['id', 'album', 'song', 'position']


class MusicManagerUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = MusicManagerUser
        fields = ['id', 'user', 'display_name', 'permissions']
