from rest_framework import serializers

from accounts.models import User
from chat.models import ChatRoom, Message
from products.serializers import ProductSerializerForRead


class SimpleUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        exclude = ('password',)

class MessageSerializer(serializers.ModelSerializer):
    sender = SimpleUserSerializer(read_only=True)
    class Meta:
        model = Message
        fields = "__all__"

class ChatRoomSerializer(serializers.ModelSerializer):
    # SerializerMethodField는 ChatRoom 필드에 더해 추가적으로 반환되는 필드들이다
    # read-only라서 저장은 되지 않는다 (.save()에 안쓰임)
    latest_message = serializers.SerializerMethodField()
    latest_message_timestamp = serializers.SerializerMethodField()
    opponent_username = serializers.SerializerMethodField()
    shop_user = SimpleUserSerializer(read_only=True)
    visitor_user = SimpleUserSerializer(read_only=True)
    messages = MessageSerializer(many=True, read_only=True, source='messages.all')
    product = ProductSerializerForRead(read_only=True)

    class Meta:
        model = ChatRoom
        fields = ('id', 'shop_user', 'visitor_user', 'latest_message', 'latest_message_timestamp', 'opponent_username', 'messages', 'product')

    # get_<method_field> 메서드 파라미터 안에 있는 obj는 ChatRoom 객체이다

    def get_latest_message(self, obj):
        # 최신 메시지 가져오기
        latest_msg = Message.objects.filter(room=obj).order_by('-timestamp').first()
        if latest_msg:
            return latest_msg.text
        else:
            return None
        
    def get_latest_message_timestamp(self, obj):
        # 최신 메시지 시간 가져오기
        latest_msg = Message.objects.filter(room=obj).order_by('-timestamp').first()
        if latest_msg:
            return latest_msg.timestamp
        else:
            return None

    def get_opponent_username(self, obj):
        # 요청 사용자와 대화하는 상대방의 닉네임 가져오기
        request_user_email = self.context['request'].query_params.get('email', None)
        if request_user_email is None:
            return None
        if request_user_email == obj.shop_user.email:
            return obj.visitor_user.username
        else:
            return obj.shop_user.username

    # def get_shop_user_username(self, obj):
    #     return obj.shop_user.username
    #
    # def get_visitor_user_username(self, obj):
    #     return obj.visitor_user.username
