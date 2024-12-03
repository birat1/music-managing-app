# Seeding carries no marks but may help you write your tests
import json
import os
from django.core.management.base import BaseCommand
from label_music_manager.models import Album, Song, AlbumTracklistItem

class Command(BaseCommand):
    help = 'Insert sample data into database for tests'

    def handle(self, *args, **options):
        Album.objects.all().delete()
        Song.objects.all().delete()
        AlbumTracklistItem.objects.all().delete()

        json_file_path = os.path.join(os.path.dirname(__file__), '../sample_data.json')
        try:
            with open(json_file_path, 'r') as file:
                data = json.load(file)
        except FileNotFoundError:
            self.stdout.write(self.style.ERROR('sample_data.json not found at {}'.format(json_file_path)))
            return

        # Iterate over albums
        for album_data in data['albums']:
            album, created = Album.objects.get_or_create(
                title=album_data['title'],
                description=album_data['description'],
                artist=album_data['artist'],
                price=album_data['price'],
                format=album_data['format'],
                release_date=album_data['release_date'],
            )

            # Check for cover image and set it
            if 'cover' in album_data and album_data['cover']:
                album.cover_image = album_data['cover']
                album.save()

            if created:
                self.stdout.write(self.style.SUCCESS(f'Album "{album.title}" created.'))

        # Create songs and associate them with albums
        for song_data in data['songs']:
            song, created = Song.objects.get_or_create(
                title=song_data['title'],
                length=song_data['runtime']
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'Song "{song.title}" created.'))

            # Associate songs with albums through AlbumTracklistItem
            for album_title in song_data['albums']:
                albums_with_title = Album.objects.filter(title=album_title)
                if not albums_with_title:
                    self.stdout.write(self.style.WARNING(f'No albums found with title "{album_title}".'))
                for album in albums_with_title:
                    AlbumTracklistItem.objects.get_or_create(
                        album=album,
                        song=song
                    )
                    self.stdout.write(self.style.SUCCESS(f'Added song "{song.title}" to album "{album.title}".'))
