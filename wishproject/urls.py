from django.contrib import admin
from django.urls import include, path
from django.conf.urls.static import static
from django.conf import settings
from rest_framework import routers
from rest_framework.authtoken.views import obtain_auth_token
from wishapi.views import (
    UserViewSet,
    WishlistViewSet,
    PriorityViewSet,
    ProfileViewSet,
    FriendViewSet,
    WishlistItemViewSet,
    PurchaseViewSet,
)


router = routers.DefaultRouter(trailing_slash=False)
router.register(r"wishlists", WishlistViewSet, "wishlist")
router.register(r"priorities", PriorityViewSet, "priority")
router.register(r"profile", ProfileViewSet, "profile")
router.register(r"friends", FriendViewSet, "friend")
router.register(r"wishlist_items", WishlistItemViewSet, "wishlist_item")
router.register(r"purchases", PurchaseViewSet, "purchase")

urlpatterns = [
    path("", include(router.urls)),
    path("login", UserViewSet.as_view({"post": "user_login"}), name="login"),
    path(
        "register", UserViewSet.as_view({"post": "register_account"}), name="register"
    ),
    path("api-token-auth", obtain_auth_token),
    path("api-auth", include("rest_framework.urls", namespace="rest_framework")),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
