# Write your models here
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.text import slugify
from django.core.exceptions import ValidationError
from datetime import date, timedelta


def validate_release_date(release_date):
    max_future_date = date.today() + timedelta(days=3*365)

    if release_date > max_future_date:
        raise ValidationError(
            'Release date cannot be more than 3 years in the future')


class Album(models.Model):
    FORMAT_CHOICES = [
        ('DD', 'Digital Download'),
        ('CD', 'CD'),
        ('VL', 'Vinyl'),
    ]

    cover_image = models.ImageField(default='no_cover.jpg')
    title = models.CharField(max_length=512, blank=False)
    description = models.TextField(blank=True)
    artist = models.CharField(max_length=512, blank=False)
    price = models.DecimalField(max_digits=5, decimal_places=2, blank=False, validators=[MinValueValidator(0), MaxValueValidator(999.99)])
    format = models.CharField(max_length=2, choices=FORMAT_CHOICES)
    release_date = models.DateField(validators=[validate_release_date])
    slug = models.SlugField(blank=True)
    tracks = models.ManyToManyField('Song', through='AlbumTracklistItem')

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    class Meta:
        unique_together = ['title', 'artist', 'format']


class Song(models.Model):
    title = models.CharField(max_length=512, blank=False)
    length = models.PositiveIntegerField(blank=False, validators=[MinValueValidator(10)])

    def __str__(self):
        return self.title


class AlbumTracklistItem(models.Model):
    album = models.ForeignKey(Album, on_delete=models.CASCADE)
    song = models.ForeignKey(Song, on_delete=models.CASCADE)
    position = models.PositiveIntegerField(blank=True, null=True)

    class Meta:
        unique_together = ['album', 'song']
        ordering = ['position']

    def __str__(self):
        return f'{self.album.title} - {self.song.title}'


class MusicManagerUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    display_name = models.CharField(max_length=512, blank=False)

    class Meta:
        permissions = [
            ('Artist', 'artist'),
            ('Editor', 'editor'),
            ('Viewer', 'viewer')
        ]

    def __str__(self):
        return f'{self.user.username} [{self.display_name}]'
