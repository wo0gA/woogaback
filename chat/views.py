from rest_framework import generics, serializers, status
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from chat.models import ChatRoom, Message
from chat.models import ShopUser, VisitorUser
from accounts.models import User
from chat.serializers import ChatRoomSerializer, MessageSerializer

from django.http import Http404, JsonResponse
from django.conf import settings

# Create your views here.
class ImmediateResponseException(Exception):
    # 사용자 정의 예외 클래스로, 예외가 발생할 때 즉각적인 HTTP 응답을 생성하기 위해 사용됨
    def __init__(self, response):
        # 예외 인스턴스를 생성할 때 HTTP 응답 객체를 받는다
        self.response = response

class ChatRoomListCreateView(generics.ListCreateAPIView):
    serializer_class = ChatRoomSerializer

    def get_queryset(self):
        try:
            user_email = self.request.query_params.get('email', None)

            if not user_email:
                raise ValidationError('Email 파라미터가 필요합니다.')

            return ChatRoom.objects.filter(
                shop_user__email=user_email
            ) | ChatRoom.objects.filter(
                visitor_user__email=user_email
            )
        except ValidationError as e:
            # email 파라미터가 없을 때
            content = {'detail': e.detail}
            return Response(content, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            # email이 잘못되었거나 다른 종류의 예외 발생
            content = {'detail': str(e)}
            return Response(content, status=status.HTTP_400_BAD_REQUEST)

    def get_serializer_context(self):
        # 시리얼라이저에 request 관련 정보를 추가로 전달
        context = super(ChatRoomListCreateView, self).get_serializer_context()
        context['request'] = self.request
        return context

    def create(self, request, *args, **kwargs):
        # POST 요청을 처리해 새로운 리소스 생성

        # 요청 데이터로부터 시리얼라이저 생성
        serializer = self.get_serializer(data=request.data)
        # 시리얼라이저 유효성 검사, 유효하지 않다면 예외 발생
        serializer.is_valid(raise_exception=True)
        try:
            # 시리얼라이저를 통해 데이터 저장
            self.perform_create(serializer)
        except ImmediateResponseException as e:
            return e.response

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def perform_create(self, serializer):
        shop_user_email = self.request.data.get('shop_user_email')
        visitor_user_email = self.request.data.get('visitor_user_email')

        shop_user, _ = ShopUser.objects.get_or_create(shop_user_email=shop_user_email)
        visitor_user, _ = VisitorUser.objects.get_or_create(visitor_user_email=visitor_user_email)

        # try:
        #     shop_user = User.objects.get(email=shop_user_email)
        # except User.DoesNotExist as e:
        #     content = {'detail': "물건 주인의 이메일을 User에서 찾을 수 없습니다."}
        #     raise ImmediateResponseException(Response(content, status=status.HTTP_400_BAD_REQUEST))
        # try:
        #     visitor_user = User.objects.get(email=visitor_user_email)
        # except User.DoesNotExist as e:
        #     content = {'detail': "구매/대여 희망자의 이메일을 User에서 찾을 수 없습니다."}
        #     raise ImmediateResponseException(Response(content, status=status.HTTP_400_BAD_REQUEST))

        # 두 이메일을 가진 채팅방이 이미 있는지 확인합니다.
        existing_chatroom = ChatRoom.objects.filter(
            shop_user__email=shop_user_email, visitor_user__email=visitor_user_email
        ).first()
        # 이미 존재하는 채팅방이 있다면 해당 채팅방의 정보를 시리얼라이즈하여 응답합니다.
        if existing_chatroom:
            serializer = ChatRoomSerializer(existing_chatroom, context={'request': self.request})
            raise ImmediateResponseException(Response(serializer.data, status=status.HTTP_200_OK))

        serializer.save(shop_user=shop_user, visitor_user=visitor_user)

class MessageListView(generics.ListAPIView):
    serializer_class = MessageSerializer

    def get_queryset(self):
        # URL 파라미터에서 room_id 값 가져오기
        room_id = self.kwargs.get('room_id')
        # room_id 파라미터가 없다면 400 에러 반환
        if not room_id:
            content = {'detail': 'room_id 파라미터가 필요합니다.'}
            return Response(content, status=status.HTTP_400_BAD_REQUEST)

        # room_id에 해당하는 메시지들을 반환 (없으면 빈 리스트)
        return Message.objects.filter(room_id=room_id)
