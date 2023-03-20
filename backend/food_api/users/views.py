from djoser import utils
from djoser.serializers import TokenSerializer
from djoser.views import TokenCreateView, UserViewSet
from rest_framework import permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Subscription, User
from .serializers import SubscriptionSerializer, CustomUserSerializer


class MyTokenCreateView(TokenCreateView):
    def _action(self, serializer):
        token = utils.login_user(self.request, serializer.user)
        token_serializer_class = TokenSerializer
        return Response(
            data=token_serializer_class(token).data,
            status=status.HTTP_201_CREATED
            )


class Logout(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        request.user.auth_token.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class CustomUserViewSet(UserViewSet):
    queryset = User.objects.all()
    serializer_class = CustomUserSerializer  # новый серик 20.03.23

    # ендпойнт subscribe
    @action(methods=['post', 'delete'], detail=True, url_path='subscribe',
            serializer_class=SubscriptionSerializer)
    def subscribe(self, request, id):
        if request.method == 'POST':
            # проверка на подписку на себя -- отказать
            if request.user.id == int(id):
                return Response({'errors': 'На cебя не подписываем'},
                                status=status.HTTP_400_BAD_REQUEST)
            # проверка на повторность подписки
            elif (Subscription.objects.filter
                  (followed=id, follower=request.user.id).exists()):
                return Response({'errors': 'Вы уже подписаны на этого автора,\
                                повторная подписка невозможна'},
                                status=status.HTTP_400_BAD_REQUEST)
            # запись в базу подписки
            else:
                followed_author = User.objects.get(id=int(id))
                serializer = SubscriptionSerializer(
                    followed_author,
                    data={'username': followed_author.username,
                          'email': followed_author.email,
                          'id': followed_author.id,
                          'last_name': followed_author.last_name,
                          'first_name': followed_author.first_name},
                    context={'request': request})
                serializer.is_valid(raise_exception=True)
                Subscription.objects.create(follower=request.user,
                                            followed=followed_author)
                return Response(serializer.data,
                                status=status.HTTP_201_CREATED)
        else:
            try:
                Subscription.objects.get(followed=id,
                                         follower=request.user.id).delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            except Subscription.DoesNotExist:
                return Response({'errors': 'Подписки и не было.\
                                 Отписаться не можем'},
                                status=status.HTTP_400_BAD_REQUEST)

    @action(methods=['get'], detail=False,
            serializer_class=SubscriptionSerializer)
    def subscriptions(self, request):
        user = request.user
        # список тех, на кого подписан текущий user
        followeds = User.objects.filter(subscription_followed__follower=user)
        output = self.paginate_queryset(followeds)
        serializer = SubscriptionSerializer(output, many=True,
                                            context={'request': request})
        return self.get_paginated_response(serializer.data)
