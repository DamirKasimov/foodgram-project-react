from djoser.views import TokenCreateView
from djoser.serializers import TokenSerializer
from rest_framework import status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from djoser import utils
from .models import User, Subscription
from .serializers import SubscriptionSerializer
from rest_framework.decorators import action
from djoser.views import UserViewSet


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
    queryset = Subscription.objects.all()
    serializer_class = SubscriptionSerializer

    # ендпойнт subscribe
    @action(methods=['post', 'delete'], detail=True,
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

    @action(methods=['get'], detail=False)
    def subscriptions(self, request):
        user = request.user
        # список тех, на кого подписан текущий user
        followeds = User.objects.filter(subscription_followed__follower=user)
        output = self.paginate_queryset(followeds)
        serializer = SubscriptionSerializer(output, many=True,
                                            context={'request': request})
        return self.get_paginated_response(serializer.data)
