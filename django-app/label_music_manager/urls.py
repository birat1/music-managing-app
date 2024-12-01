# Use this file to specify your subapp's routes
from django.contrib.auth.views import LogoutView
from django.urls import include, path
from rest_framework.routers import DefaultRouter
from .views import AlbumListView, AlbumDetailView, AlbumEditView, AlbumDeleteView, AlbumCreateView
from .api_views import AlbumViewSet, SongViewSet, AlbumTracklistViewSet

router = DefaultRouter()
router.register(r'albums', AlbumViewSet, basename='albums')
router.register(r'songs', SongViewSet, basename='songs')
router.register(r'tracklist', AlbumTracklistViewSet, basename='tracklist')

urlpatterns = [
    # Templated views
    path('', AlbumListView.as_view(), name='album_list'),
    path('albums/<int:id>/', AlbumDetailView.as_view(), name='album_detail'),
    # path('albums/<int:id>/<slug:slug>/', AlbumDetailView.as_view(), name='album_detail_slug'),
    path('albums/new/', AlbumCreateView.as_view(), name='album_create'),
    path('albums/<int:id>/edit/', AlbumEditView.as_view(), name='album_edit'),
    path('albums/<int:id>/delete/', AlbumDeleteView.as_view(), name='album_delete'),

    # API endpoints
    path('api/', include(router.urls)),

    path('accounts/logout/', LogoutView.as_view(), name='logout'),
]
