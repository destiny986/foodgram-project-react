from django.urls import include, path
from rest_framework.routers import SimpleRouter

from .views import (
    FollowUserViewSet,
    FollowViewSet,
    IngredientsViewSet,
    RecipesViewSet,
    TagViewSet,
)

router_v1 = SimpleRouter()
router_v1.register("users/subscriptions", FollowViewSet, basename="follow")
router_v1.register("users", FollowUserViewSet, basename="users_follow")
router_v1.register("ingredients", IngredientsViewSet, basename="ingredients")
router_v1.register("tags", TagViewSet, basename="tags")
router_v1.register("recipes", RecipesViewSet, basename="recipes")

urlpatterns = [
    path("", include(router_v1.urls)),
    path("", include("djoser.urls")),
    path("auth/", include("djoser.urls.authtoken")),
]
