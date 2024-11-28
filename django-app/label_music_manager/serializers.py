# Write your serializers here
from rest_framework import serializers
from .models import Album, Song, AlbumTracklistItem, MusicManagerUser


class SongSerializer(serializers.ModelSerializer):
    class Meta:
        model = Song
        fields = ['id', 'title', 'length']


class AlbumSerializer(serializers.ModelSerializer):
    tracks = SongSerializer(many=True, read_only=True)
    short_description = serializers.SerializerMethodField()
    release_year = serializers.SerializerMethodField()
    total_playtime = serializers.SerializerMethodField()

    class Meta:
        model = Album
        fields = [
            'id',
            'cover_image',
            'title',
            'description',
            'short_description',
            'artist',
            'price',
            'format',
            'release_date',
            'release_year',
            'slug',
            'tracks',
            'total_playtime'
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
