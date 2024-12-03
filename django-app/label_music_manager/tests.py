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
        # Create an album object
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
        # Create a song object
        song = Song.objects.create(
            title='Test Song',
            length=120,
        )

        self.assertEqual(song.title, 'Test Song')
        self.assertEqual(song.length, 120)

    def test_song_length_validation(self):
        # Song length must be greater than 10 seconds
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

class AlbumViewTest(TestCase):
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
        self.album1 = Album.objects.create(
            cover_image='dripping-stereo.png',
            title='Test Album',
            artist='Artist',
            price=9.99,
            format='CD',
            release_date=date.today(),
        )
        self.song1 = Song.objects.create(
            title='Test Song 1',
            length=120,
        )
        self.tracklist_item = AlbumTracklistItem.objects.create(
            album=self.album1,
            song=self.song1,
            position=1
        )

        # Create an empty album
        self.album2 = Album.objects.create(
            cover_image='sealife.png',
            title='Sealife',
            artist='Artist2',
            price=14.99,
            format='VL',
            release_date=date.today(),
        )

    def test_unauthenticated_user_can_view_all_albums(self):
        response = self.client.get(reverse('album_list'))
        self.assertEqual(response.status_code, 200)

    def test_artist_can_only_view_own_albums(self):
        self.client.login(username='artist', password='password')
        response = self.client.get(reverse('album_list'))
        self.assertEqual(response.status_code, 200)
        albums = response.context['albums']
        self.assertEqual(list(albums), [self.album1])

    def test_viewer_editor_can_view_all_albums(self):
        self.client.login(username='viewer', password='password')
        response = self.client.get(reverse('album_list'))
        self.assertEqual(response.status_code, 200)
        albums = response.context['albums']
        self.assertEqual(list(albums), [self.album1, self.album2])

        self.client.login(username='editor', password='password')
        response = self.client.get(reverse('album_list'))
        self.assertEqual(response.status_code, 200)
        albums = response.context['albums']
        self.assertEqual(list(albums), [self.album1, self.album2])

    def test_album_detail_view_without_login_redirects(self):
        response = self.client.get(reverse('album_detail', args=[self.album1.id]))
        self.assertEqual(response.status_code, 302)

    def test_album_detail_view_with_invalid_id(self):
        self.client.login(username='viewer', password='password')
        response = self.client.get(reverse('album_detail', args=[100]))
        self.assertEqual(response.status_code, 404)

    def test_viewer_artist_editor_album_detail_view(self):
        self.client.login(username='viewer', password='password')
        response = self.client.get(reverse('album_detail', args=[self.album1.id]))
        self.assertEqual(response.status_code, 200)
        album = response.context['album']
        self.assertEqual(album, self.album1)

        self.client.login(username='artist', password='password')
        response = self.client.get(reverse('album_detail', args=[self.album1.id]))
        self.assertEqual(response.status_code, 200)
        album = response.context['album']
        self.assertEqual(album, self.album1)

        self.client.login(username='editor', password='password')
        response = self.client.get(reverse('album_detail', args=[self.album1.id]))
        self.assertEqual(response.status_code, 200)
        album = response.context['album']
        self.assertEqual(album, self.album1)

    def test_album_edit_view_without_login_redirects(self):
        response = self.client.get(reverse('album_edit', args=[self.album1.id]))
        self.assertEqual(response.status_code, 302)

    def test_album_edit_view_with_invalid_id(self):
        self.client.login(username='editor', password='password')
        response = self.client.get(reverse('album_edit', args=[100]))
        self.assertEqual(response.status_code, 404)

    def test_viewer_cannot_edit_any_albums(self):
        self.client.login(username='viewer', password='password')
        with self.assertRaises(PermissionDenied):
            self.client.get(reverse('album_edit', args=[self.album1.id]))

    def test_artist_can_only_edit_own_albums(self):
        self.client.login(username='artist', password='password')
        with self.assertRaises(PermissionDenied):
            self.client.get(reverse('album_edit', args=[self.album2.id]))

        # Own album
        response = self.client.get(reverse('album_edit', args=[self.album1.id]))
        self.assertEqual(response.status_code, 200)

    def test_editor_can_edit_any_albums(self):
        self.client.login(username='editor', password='password')
        response = self.client.get(reverse('album_edit', args=[self.album1.id]))
        self.assertEqual(response.status_code, 200)

        response = self.client.get(reverse('album_edit', args=[self.album2.id]))
        self.assertEqual(response.status_code, 200)

    def test_album_edit_success(self):
        self.client.login(username='editor', password='password')
        response = self.client.post(reverse('album_edit', args=[self.album1.id]), {
            'cover_image': 'dripping-stereo.png',
            'title': 'Updated Title',
            'artist': 'Artist Name',
            'price': 20,
            'format': 'VL',
            'release_date': '2023-01-01',
        })
        self.assertRedirects(response, reverse('album_detail', args=[self.album1.id]))
        self.album1.refresh_from_db()
        self.assertEqual(self.album1.title, 'Updated Title')

    def test_album_edit_with_invalid_data(self):
        self.client.login(username='editor', password='password')
        response = self.client.post(reverse('album_edit', args=[self.album1.id]), {
            'title': '',
            'cover_image': '',
            'description': 'Updated Description',
            'artist': 'Test Artist',
            'price': 10.99,
            'format': 'CD',
            'release_date': '2023-01-01'
        })
        self.assertEqual(response.status_code, 200)

        # Ensure the form contains a validation error for the title
        form = response.context['form']
        self.assertIn('title', form.errors)
        self.assertEqual(form.errors['title'], ['This field is required.'])

    def test_album_delete_view_without_login_redirects(self):
        response = self.client.get(reverse('album_delete', args=[self.album1.id]))
        self.assertEqual(response.status_code, 302)

    def test_viewer_cannot_delete_albums(self):
        self.client.login(username='viewer', password='password')
        with self.assertRaises(PermissionDenied):
            self.client.get(reverse('album_delete', args=[self.album1.id]))

    def test_artist_cannot_delete_own_album(self):
        self.client.login(username='artist', password='password')
        with self.assertRaises(PermissionDenied):
            self.client.get(reverse('album_delete', args=[self.album1.id]))

    def test_editor_can_delete_any_albums(self):
        self.client.login(username='editor', password='password')
        response = self.client.post(reverse('album_delete', args=[self.album1.id]))
        self.assertRedirects(response, reverse('album_list'))
        self.assertFalse(Album.objects.filter(id=self.album1.id).exists())

    def test_editor_attempts_to_delete_nonexistent_album(self):
        self.client.login(username='editor', password='password')
        url = reverse('album_delete', kwargs={'id': 9999})
        response = self.client.post(url)
        self.assertEqual(response.status_code, 404)

    def test_viewer_cannot_create_albums(self):
        self.client.login(username='viewer', password='password')
        with self.assertRaises(PermissionDenied):
            self.client.get(reverse('album_create'))

    def test_artist_cannot_create_albums(self):
        self.client.login(username='artist', password='password')
        with self.assertRaises(PermissionDenied):
            self.client.get(reverse('album_create'))

    def test_editor_can_create_albums(self):
        self.client.login(username='editor', password='password')
        response = self.client.post(reverse('album_create'), {
            'title': 'New Album',
            'artist': 'Artist Name',
            'cover_image': 'cover.png',
            'description': 'A wonderful album',
            'price': 12.99,
            'format': 'CD',
            'release_date': '2023-01-01'
        })
        self.assertRedirects(response, reverse('album_list'))
        self.assertTrue(Album.objects.filter(title='New Album').exists())

    def test_editor_attempts_to_create_album_with_invalid_data(self):
        self.client.login(username='editor', password='password')
        response = self.client.post(reverse('album_create'), {
            'title': '',
            'cover_image': '',
            'description': 'A wonderful album',
            'artist': 'Artist Name',
            'price': 12.99,
            'format': 'CD',
        })
        self.assertEqual(response.status_code, 200)

        # Ensure the form contains a validation error for the title
        form = response.context['form']
        self.assertIn('title', form.errors)
        self.assertEqual(form.errors['title'], ['This field is required.'])
