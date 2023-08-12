from django.urls import include, path
from rest_framework.routers import SimpleRouter

from .views import FollowViewSet, FollowUserViewSet


router_v1 = SimpleRouter()
router_v1.register(r'users/subscriptions', FollowViewSet, basename='follow')
router_v1.register(r'users', FollowUserViewSet, basename='users_follow')

urlpatterns = [
    path('', include(router_v1.urls)),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
]
