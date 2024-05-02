from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import serializers, status
from django.contrib.auth.models import User
from wishapi.models import Wishlist, WishlistItem, Priority
from django.http import HttpResponseServerError
from django.db.models import Q
from wishapi.views import UserSerializer
from rest_framework.permissions import IsAuthenticated


class WishlistItemSerializer(serializers.ModelSerializer):
    priority_name = serializers.SerializerMethodField()

    class Meta:
        model = WishlistItem
        fields = (
            "id",
            "wishlist",
            "name",
            "note",
            "website_url",
            "quantity",
            "priority",
            "priority_name",
            "creation_date",
        )

    def get_priority_name(self, obj):
        return obj.priority.name if obj.priority else None


class WishlistSerializer(serializers.ModelSerializer):
    """JSON serializer for public wishlists"""

    wishlist_items = WishlistItemSerializer(many=True, source="items_in_list")
    user = UserSerializer()

    class Meta:
        model = Wishlist
        fields = (
            "id",
            "user",
            "title",
            "description",
            "spoil_surprises",
            "address",
            "creation_date",
            "date_of_event",
            "pinned",
            "private",
            "wishlist_items",
        )


class WishlistViewSet(viewsets.ViewSet):
    """View for interacting with user wishlists"""
    permission_classes = [IsAuthenticated]

    def list(self, request):
        """
        @api {GET} /wishlists GET user's wishlists
        @apiName GetWishlists
        @apiGroup Wishlists

        @apiHeader {String} Authorization Auth token
        @apiHeaderExample {String} Authorization
            Token 9ba45f09651c5b0c404f37a2d2572c026c146611

        @apiSuccess (200) {Object[]} public_wishlists Array of public wishlist objects
        @apiSuccess (200) {id} public_wishlists.id Wishlist id
        @apiSuccess (200) {Number} public_wishlists.user User id associated with the wishlist
        @apiSuccess (200) {String} public_wishlists.title Title of the wishlist
        @apiSuccess (200) {String} public_wishlists.description Description of the wishlist
        @apiSuccess (200) {Boolean} public_wishlists.spoil_surprises Flag indicating whether surprises should be spoiled
        @apiSuccess (200) {String} public_wishlists.address Mailing address for purchased items associated with the wishlist
        @apiSuccess (200) {String} public_wishlists.creation_date Date the wishlist was created (ISO 8601 format)
        @apiSuccess (200) {String} public_wishlists.date_of_event Date of the event associated with the wishlist (ISO 8601 format)
        @apiSuccess (200) {Boolean} public_wishlists.pinned Flag indicating whether the wishlist is pinned

        @apiSuccess (200) {Object[]} private_wishlists Array of private wishlist objects
        @apiSuccess (200) {id} private_wishlists.id Wishlist id
        @apiSuccess (200) {Number} private_wishlists.user User id associated with the wishlist
        @apiSuccess (200) {String} private_wishlists.title Title of the wishlist
        @apiSuccess (200) {String} private_wishlists.description Description of the wishlist
        @apiSuccess (200) {Boolean} private_wishlists.spoil_surprises Flag indicating whether surprises should be spoiled
        @apiSuccess (200) {String} private_wishlists.address Mailing address for purchased items associated with the wishlist
        @apiSuccess (200) {String} private_wishlists.creation_date Date the wishlist was created (ISO 8601 format)
        @apiSuccess (200) {String} private_wishlists.date_of_event Date of the event associated with the wishlist (ISO 8601 format)
        @apiSuccess (200) {Boolean} private_wishlists.pinned Flag indicating whether the wishlist is pinned
        @apiSuccess {Object[]} wishlist_items Array of wishlist items associated with the wishlist

        @apiSuccessExample {json} Success
            {
                "public": [
                    {
                        "id": 3,
                        "user": 2,
                        "title": "Meg and Ryan's Wedding",
                        "description": "We are broke college students. Anything you can contribute would greatly appreciated!",
                        "spoil_surprises": true,
                        "address": "789 Oak Street, Silverwood, TX 75001",
                        "creation_date": "2024-04-26T08:00:00Z",
                        "date_of_event": "2024-05-10T08:00:00Z",
                        "pinned": false,
                        "wishlist_items": [
                            {
                                "id": 5,
                                "wishlist": 3,
                                "name": "KitchenAid Stand Mixer",
                                "note": "Preferably the Contour Silver color",
                                "website_url": "https://www.kitchenaid.com/refurbished/stand-mixers-and-attachments/p.refurbished-artisan-series-5-quart-tilt-head-stand-mixer.rrk150cu.html?region_id=LDC822&productcategory=refurbished-attachments&cmp=kad:wp_sda%7C01%7C00371%7Czz%7Csh%7Ct02%7Cp79%7Czz%7Cv04_kasa_ppc:ga:ps:txt:txt:cpc:shop_smartshop_refurbrob:na:na:20427281698::c&gad_source=1&gclid=Cj0KCQjw_qexBhCoARIsAFgBletzd1CTmWJCXTpx8jelGrcjcRbgB3DDM-B81Pycgu9XXM7Ht_ik9EEaAo5YEALw_wcB&gclsrc=aw.ds",
                                "quantity": 1,
                                "priority": 1,
                                "priority_name": "Must-Have",
                                "creation_date": "2024-04-26T08:00:00Z"
                            },
                            {
                                "id": 6,
                                "wishlist": 3,
                                "name": "Mills Waffle Bedspread and Pillow Sham Set - Levtex Home",
                                "note": "King size in grey",
                                "website_url": "https://www.target.com/p/mills-waffle-quilt-and-pillow-sham-set-levtex-home/-/A-83765488",
                                "quantity": 1,
                                "priority": 2,
                                "priority_name": "High Priority",
                                "creation_date": "2024-04-27T08:00:00Z"
                            }
                        ]
                    }
                ],
                "private": [
                    {
                        "id": 4,
                        "user": 2,
                        "title": "Outdoor Adventure Wishlist",
                        "description": "Gear and equipment for epic outdoor adventures!",
                        "spoil_surprises": false,
                        "address": "101 Pine Street, Sunnydale, FL 33001",
                        "creation_date": "2024-04-27T08:00:00Z",
                        "date_of_event": "2024-06-15T08:00:00Z",
                        "pinned": false,
                        "wishlist_items": []
                    }
                ]
        }
        """
        search_text = request.query_params.get("q", None)
        try:
            user = request.auth.user
            if search_text:
                public_wishlists = Wishlist.objects.filter(
                    Q(title__contains=search_text)
                    | Q(description__contains=search_text),
                    private=False,
                    user=user,
                )
                private_wishlists = Wishlist.objects.filter(
                    Q(title__contains=search_text)
                    | Q(description__contains=search_text),
                    private=True,
                    user=user,
                )
            else:
                public_wishlists = Wishlist.objects.filter(private=False, user=user)
                private_wishlists = Wishlist.objects.filter(private=True, user=user)

            public_serializer = WishlistSerializer(
                public_wishlists, many=True, context={"request": request}
            )
            private_serializer = WishlistSerializer(
                private_wishlists, many=True, context={"request": request}
            )

            return Response(
                {
                    "public": public_serializer.data,
                    "private": private_serializer.data,
                }
            )

        except Exception as ex:
            return HttpResponseServerError(ex)

    def retrieve(self, request, pk=None):
        """
        Retrieve details of a single wishlist.

        @api {GET} wishlists/:id Retrieve Single Wishlist
        @apiName RetrieveWishlist
        @apiGroup Wishlists

        @apiHeader {String} Authorization Auth token
        @apiHeaderExample {String} Authorization:
            Token d74b97fbe905134520bb236b0016703f50380dcf

        @apiParam {Number} pk Wishlist's unique ID.

        @apiSuccess {Number} id Wishlist ID.
        @apiSuccess {Number} user User ID.
        @apiSuccess {String} title Wishlist title.
        @apiSuccess {String} description Wishlist description.
        @apiSuccess {Boolean} spoil_surprises Indicates if surprises should be spoiled.
        @apiSuccess {String} address Wishlist address.
        @apiSuccess {String} creation_date Date the wishlist was created (ISO 8601 format).
        @apiSuccess {String} date_of_event Date of the event associated with the wishlist (ISO 8601 format).
        @apiSuccess {Boolean} pinned Indicates if the wishlist is pinned.
        @apiSuccess {Object[]} wishlist_items Array of wishlist items associated with the wishlist

        @apiSuccessExample {json} Success:
            HTTP/1.1 200 OK
        {
            "id": 1,
            "user": 1,
            "title": "My Birthday 40th birthday",
            "description": "I am turning 40! Here are a few things I like",
            "spoil_surprises": true,
            "address": "123 Main Street, Aurora Springs, CA 90210",
            "creation_date": "2024-04-26T08:00:00Z",
            "date_of_event": "2024-05-10T08:00:00Z",
            "pinned": false,
            "wishlist_items": [
                {
                    "id": 1,
                    "wishlist": 1,
                    "name": "Portable Espresso Maker",
                    "note": "Preferably in red color; with a sleek design",
                    "website_url": "https://www.amazon.com/Minipresso-Portable-Espresso-Compatible-Manually/dp/B00VTA9F6U/ref=sr_1_2_sspa?dib=eyJ2IjoiMSJ9.YwUMDQDZQFoNOEtk2iAQHyxl5ryMvWwsjVN6NVGa7-sKfv5jhbVW8MB0X_vgYf84AoXQNAoTpDD8--6ssHb-JA8ct0Yt8uAnIySJrbQdhlk5g3RwaDTrEqoJ0CSLdX9cZuPvpdyknGvQp8sb1LKVda4iU0fsMm5OSsC6ARewqi6cNSo-esoTwDscs5-CJZJhaPEVmytRp7go2SfkkPD2LXyviV6vCbP6oDuvyoLl_A1t45ZG-N1P0gR-92MTFKC66ariZxJvZB4Mjfmsi7dlmcUrIDtZ0d55XxtczC_QnPw.7ofluAMDRcYlazmZnAmo9iueXtfNqA6nNBcOlBURsyU&dib_tag=se&hvadid=557264626784&hvdev=c&hvlocphy=9013137&hvnetw=g&hvqmt=e&hvrand=9871293913452938991&hvtargid=kwd-400415586212&hydadcr=4919_13166229&keywords=espresso+on+the+go+machine&qid=1714074520&sr=8-2-spons&sp_csd=d2lkZ2V0TmFtZT1zcF9hdGY&psc=1",
                    "quantity": 2,
                    "priority": 1,
                    "priority_name": "Must-Have",
                    "creation_date": "2024-04-26T08:00:00Z"
                },
                {
                    "id": 2,
                    "wishlist": 1,
                    "name": "Leatherbound Journals",
                    "note": "Plain, classic design; preferably with lined pages",
                    "website_url": "https://www.amazon.com/FOCUS-DAY-Notebooks-Hardcover-Multicolor/dp/B0CKSDF4GJ/ref=sr_1_9?crid=RYOHD217TFR6&dib=eyJ2IjoiMSJ9.dJECXHOwnr0gQcbiV7_JzR96bZvi9HZIh6FCPvKbB6dzsneoIZ9RpTdpU4yGZNZ59h4VgBhGzQxKDwT6inhOp7_n-WfTj9ddctu3D54u8Wt4bX7G3iSbnW99j1G7sARcwwo1bbyHM17EUlRJCcvxH4KTcH6o5qU-oAP6QVG2ar8UoTYefjKmx8aoxEnt5WzMFF0ggdeqHj0bJ7tgivNTtr5iq8dIh1mEl_TcD7ZyDxZ3WmtzKvrablHsAvWtSCpld08e00r7dQ53_ju22gqZHgWmZ8EUg0pJnyZVFnyZqi8.pf5UI6c-p25X2_NW7_Zh-jy8K4_29RfiPADpiVE7F6w&dib_tag=se&keywords=Leather-bound+Journal+Set&qid=1714074619&sprefix=leather-bound+journal+set%2Caps%2C133&sr=8-9",
                    "quantity": 2,
                    "priority": 4,
                    "priority_name": "Low Priority",
                    "creation_date": "2024-04-27T08:00:00Z"
                }
            ]
        }
        """

        try:
            # Retrieve the wishlist object
            wishlist = Wishlist.objects.get(pk=pk)

            # Retrieve all items associated with the wishlist
            queryset = wishlist.items_in_list.all()
            search_text = request.query_params.get("q", None)
            priority_level = request.query_params.get("priority_level", None)

            # Apply filters based on search text and priority level
            if search_text:
                queryset = queryset.filter(Q(name__icontains=search_text))
            if priority_level:
                queryset = queryset.filter(priority__name=priority_level)

            # Serialize the wishlist object
            wishlist_serializer = WishlistSerializer(
                wishlist, context={"request": request}
            )
            wishlist_data = wishlist_serializer.data

            # Serialize the filtered items
            items_serializer = WishlistItemSerializer(
                queryset, many=True, context={"request": request}
            )
            items_data = items_serializer.data

            # Combine wishlist data with filtered items data
            wishlist_data["wishlist_items"] = items_data

            return Response(wishlist_data)

        except Wishlist.DoesNotExist:
            return Response(
                {
                    "message": "The requested wishlist does not exist, or you do not have permission to access it."
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        except Exception as ex:
            return HttpResponseServerError(ex)

    def create(self, request):
        """
        Create a new wishlist.

        @api {POST} wishlists/ Create Wishlist
        @apiName CreateWishlist
        @apiGroup Wishlists

        @apiHeader {String} Authorization Auth token
        @apiHeaderExample {String} Authorization:
            Token d74b97fbe905134520bb236b0016703f50380dcf

        @apiParam {String} title Wishlist title.
        @apiParam {String} description Wishlist description.
        @apiParam {Boolean} spoil_surprises Indicates if surprises should be spoiled.
        @apiParam {Boolean} private Indicates if the wishlist is private.
        @apiParam {String} date_of_event (Optional) Date of the event associated with the wishlist (ISO 8601 format).
        @apiParam {String} address (Optional) Wishlist address.

        @apiSuccess {Number} id Wishlist ID.
        @apiSuccess {Number} user User ID.
        @apiSuccess {String} title Wishlist title.
        @apiSuccess {String} description Wishlist description.
        @apiSuccess {Boolean} spoil_surprises Indicates if surprises should be spoiled.
        @apiSuccess {String} address Wishlist address.
        @apiSuccess {String} creation_date Date the wishlist was created (ISO 8601 format).
        @apiSuccess {String} date_of_event Date of the event associated with the wishlist (ISO 8601 format).
        @apiSuccess {Boolean} pinned Indicates if the wishlist is pinned.
        @apiSuccess {Object[]} wishlist_items Array of wishlist items associated with the wishlist

        @apiSuccessExample {json} Success:
            HTTP/1.1 201 Created
        {
            "id": 1,
            "user": 1,
            "title": "My Birthday 40th birthday",
            "description": "I am turning 40! Here are a few things I like",
            "spoil_surprises": true,
            "address": "123 Main Street, Aurora Springs, CA 90210",
            "creation_date": "2024-04-26T08:00:00Z",
            "date_of_event": "2024-05-10T08:00:00Z",
            "pinned": false,
            "wishlist_items": []
        }
        """

        new_list = Wishlist()
        # Get the data from the client's JSON payload
        new_list.title = request.data.get("title")
        new_list.description = request.data.get("description")
        new_list.spoil_surprises = request.data.get("spoil_surprises")
        new_list.private = request.data.get("private")
        new_list.date_of_event = request.data.get("date_of_event")
        new_list.address = request.data.get("address")

        user = request.auth.user
        new_list.user = user

        try:

            new_list.save()

            serializer = WishlistSerializer(new_list, context={"request": request})
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        except Exception as ex:
            return Response({"reason": ex.args[0]}, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk=None):
        """
        @api {DELETE} /wishlists/:id DELETE wishlist instance
        @apiName DeleteWishlist
        @apiGroup Wishlists

        @apiParam {Number} id Wishlist ID (route parameter) to delete
        @apiSuccessExample {json} Success
            HTTP/1.1 204 No Content
        """
        try:
            wishlist = Wishlist.objects.get(pk=pk)
        except Wishlist.DoesNotExist:
            return Response(
                "Wishlist instance not found", status=status.HTTP_404_NOT_FOUND
            )
        
        # Check if the authenticated user is the owner of the wishlist
        if wishlist.user != request.user:
            return Response(
                "You are not authorized to delete this wishlist",
                status=status.HTTP_403_FORBIDDEN
            )

        wishlist.delete()

        return Response({}, status=status.HTTP_204_NO_CONTENT)
