from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.mixins import CreateModelMixin, DestroyModelMixin
from rest_framework.viewsets import ReadOnlyModelViewSet, GenericViewSet, ViewSet
from rest_framework.viewsets import ModelViewSet
from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet


from .serializers import FollowSerializer, FollowCreateDeleteSerializer
from users.models import Follow, User

# IsAuthenticated default
class FollowViewSet(ReadOnlyModelViewSet):
    serializer_class = FollowSerializer

    def get_queryset(self):
        return User.objects.filter(following__user=self.request.user)   # <===== self.request.user.follower.all()


class FollowUserViewSet(UserViewSet):
    @action(detail=True, methods=['post'], name='Create follow')
    def subscribe(self, request, *args, **kwargs):
        author = get_object_or_404(User, id=kwargs['id'])               # проверит на наличие автора
        serializer = FollowCreateDeleteSerializer(
            data={'user': request.user.id, 'author': author.id},
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        Follow.objects.create(user=request.user, author=author)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


    @subscribe.mapping.delete
    def destroy(self, request, *args, **kwargs):
        following_id = self.kwargs.get('id')
        object = get_object_or_404(Follow, user=request.user, author=following_id)
        object.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


'''
class FollowCreateDeleteViewSet(CreateModelMixin, DestroyModelMixin, GenericViewSet):
    serializer_class = FollowCreateDeleteSerializer

    # https://stackoverflow.com/questions/34661853/django-rest-framework-this-field-is-required-with-required-false-and-unique
    @action(detail=True, methods=['post'], name='Create follow')
    def subscribe(self, request, *args, **kwargs):
        following_id = self.kwargs.get('id')
        request.data.update({'user': request.user.id, 'author': following_id})

    
    @subscribe.mapping.delete
    def destroy(self, request, *args, **kwargs):
        following_id = self.kwargs.get('id')
        object = get_object_or_404(Follow, user=request.user, author=following_id)
        object.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)



class FollowCreateDeleteViewSet(ModelViewSet):
    http_method_names = ['post', 'delete']
    serializer_class = FollowCreateDeleteSerializer

    def create(self, request, *args, **kwargs):
        following_id = self.kwargs.get('id')
        request.data.update({'user': request.user.id, 'author': following_id})
        return super(FollowCreateDeleteViewSet, self).create(request, *args, **kwargs)
    
    @create.mapping.delete
    def destroy_follow(self, request, *args, **kwargs):
        following_id = self.kwargs.get('id')
        object = self.get_object_or_404(Follow, user=request.user, author=following_id)
        object.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
'''