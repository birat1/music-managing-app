# Write your tests here. Use only the Django testing framework.
from datetime import date, timedelta
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User, Permission
from rest_framework.exceptions import PermissionDenied
from .models import Album, MusicManagerUser, Song, AlbumTracklistItem

class AlbumModelTest(TestCase):
    def test_create_album(self):
        album = Album.objects.create(
            cover_image='dripping-stereo.png',
            title='Test Album',
            artist='Test Artist',
            price=9.99,
            format='CD',
            release_date=date.today() + timedelta(days=365*2),
        )
        self.assertEqual(album.title, 'Test Album')
        self.assertEqual(album.price, 9.99)
        self.assertEqual(album.format, 'CD')
        self.assertEqual(album.release_date, date.today() + timedelta(days=365*2))

    def test_album_release_date_invalidation(self):
        # Release date can not be greater than 3 years
        invalid_release_date = date.today() + timedelta(days=365*4)

        album = Album.objects.create(
            cover_image='dripping-stereo.png',
            title='Test Album',
            artist='Test Artist',
            price=9.99,
            format='CD',
            release_date=invalid_release_date,
        )
        with self.assertRaises(ValidationError):
            album.full_clean()

class SongModelTest(TestCase):
    def test_create_song(self):
        song = Song.objects.create(
            title='Test Song',
            length=120,
        )
        self.assertEqual(song.title, 'Test Song')
        self.assertEqual(song.length, 120)

    def test_song_length_validation(self):
        with self.assertRaises(ValidationError):
            song = Song.objects.create(
                title='Test Song',
                length=5,
            )
            song.full_clean()

class AlbumTracklistItemTest(TestCase):
    def setUp(self):
        # Create an album instance
        self.album = Album.objects.create(
            cover_image='dripping-stereo.png',
            title='Test Album',
            artist='Test Artist',
            price=9.99,
            format='CD',
            release_date=date.today(),
        )

        # Create a song instance
        self.song1 = Song.objects.create(
            title='Test Song 1',
            length=120,
        )

    def test_create_album_tracklist_item(self):
        # Create an album tracklist item
        tracklist_item = AlbumTracklistItem.objects.create(
            album=self.album,
            song=self.song1,
            position=1
        )

        # Assert item is created with correct attributes
        self.assertIsNotNone(tracklist_item)
        self.assertEqual(tracklist_item.album, self.album)
        self.assertEqual(tracklist_item.song, self.song1)
        self.assertEqual(tracklist_item.position, 1)

class MusicManagerUserTest(TestCase):
    def setUp(self):
        # Set up a user for testing
        self.user = User.objects.create_user(username='testuser', password='testpassword')

    def test_create_music_manager_user(self):
        # Create a MusicManagerUser instance
        music_manager_user = MusicManagerUser.objects.create(
            user=self.user,
            display_name='Test User',
        )
        self.assertIsNotNone(music_manager_user)
        self.assertEqual(music_manager_user.user, self.user)
        self.assertEqual(music_manager_user.display_name, 'Test User')

class URLPatternsTest(TestCase):
    def setUp(self):
        # Create users
        self.viewer_user = User.objects.create_user(username='viewer', password='password')
        self.artist_user = User.objects.create_user(username='artist', password='password')
        self.editor_user = User.objects.create_user(username='editor', password='password')

        self.viewer = MusicManagerUser.objects.create(user=self.viewer_user, display_name='Viewer')
        self.artist = MusicManagerUser.objects.create(user=self.artist_user, display_name='Artist')
        self.editor = MusicManagerUser.objects.create(user=self.editor_user, display_name='Editor')

        # Set their permission to editor to check if all routes work
        viewer_perm = Permission.objects.get(name='viewer')
        artist_perm = Permission.objects.get(name='artist')
        editor_perm = Permission.objects.get(name='editor')

        self.viewer_user.user_permissions.add(viewer_perm)
        self.artist_user.user_permissions.add(artist_perm)
        self.editor_user.user_permissions.add(editor_perm)

        # Create an album with tracks
        self.album = Album.objects.create(
            cover_image='dripping-stereo.png',
            title='Test Album',
            artist='Test Artist',
            price=9.99,
            format='CD',
            release_date=date.today(),
        )
        self.album2 = Album.objects.create(
            cover_image='sealife.png',
            title='Sealife',
            artist='Artist',
            price=14.99,
            format='VL',
            release_date=date.today(),
        )
        self.song1 = Song.objects.create(
            title='Test Song 1',
            length=120,
        )
        self.tracklist_item = AlbumTracklistItem.objects.create(
            album=self.album,
            song=self.song1,
            position=1
        )

    def test_album_list_url(self):
        self.client.login(username='viewer', password='password')

        response = self.client.get(reverse('album_list'))
        self.assertEqual(response.status_code, 200)

    def test_album_detail_url(self):
        self.client.login(username='viewer', password='password')

        response = self.client.get(reverse('album_detail', args=[self.album.id]))
        self.assertEqual(response.status_code, 200)

    def test_album_create_url(self):
        # Should not be able to access as viewer
        self.client.login(username='viewer', password='password')
        with self.assertRaises(PermissionDenied):
            self.client.get(reverse('album_create'))

        # Should not be able to access as artist
        self.client.login(username='artist', password='password')
        with self.assertRaises(PermissionDenied):
            self.client.get(reverse('album_create'))

        # Only editors should be able to access
        self.client.login(username='editor', password='password')
        response = self.client.get(reverse('album_create'))
        self.assertEqual(response.status_code, 200)

    def test_album_edit_url(self):
        # Should not be able to access as viewer
        self.client.login(username='viewer', password='password')
        with self.assertRaises(PermissionDenied):
            self.client.get(reverse('album_edit', args=[self.album.id]))

        # Artists cannot access other artist's albums
        self.client.login(username='artist', password='password')
        with self.assertRaises(PermissionDenied):
            self.client.get(reverse('album_edit', args=[self.album.id]))

        # Artists can only access their own albums
        response = self.client.get(reverse('album_edit', args=[self.album2.id]))
        self.assertEqual(response.status_code, 200)

        # Editors can access every album
        self.client.login(username='editor', password='password')
        response = self.client.get(reverse('album_edit', args=[self.album.id]))
        self.assertEqual(response.status_code, 200)

    def test_album_delete_url(self):
        # Should not be able to access as viewer
        self.client.login(username='viewer', password='password')
        with self.assertRaises(PermissionDenied):
            self.client.get(reverse('album_delete', args=[self.album.id]))

        # Artists cannot delete their own albums
        self.client.login(username='artist', password='password')
        with self.assertRaises(PermissionDenied):
            self.client.get(reverse('album_delete', args=[self.album2.id]))

        # Editors can delete albums
        self.client.login(username='editor', password='password')
        response = self.client.get(reverse('album_delete', args=[self.album.id]))
        self.assertEqual(response.status_code, 200)
