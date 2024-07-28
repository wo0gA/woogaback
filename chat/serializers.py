from rest_framework import serializers

from chat.models import ChatRoom, Message


class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = "__all__"

class ChatRoomSerializer(serializers.ModelSerializer):
    # SerializerMethodField는 ChatRoom 필드에 더해 추가적으로 반환되는 필드들이다
    # read-only라서 저장은 되지 않는다 (.save()에 안쓰임)
    latest_message = serializers.SerializerMethodField()
    opponent_email = serializers.SerializerMethodField()
    shop_user_email = serializers.SerializerMethodField()
    visitor_user_email = serializers.SerializerMethodField()
    messages = MessageSerializer(many=True, read_only=True, source='messages.all')

    class Meta:
        model = ChatRoom
        fields = ('id', 'shop_user_email', 'visitor_user_email', 'latest_message', 'opponent_email', 'messages')

    # get_<method_field> 메서드 파라미터 안에 있는 obj는 ChatRoom 객체이다

    def get_latest_message(self, obj):
        # 최신 메시지 가져오기
        latest_msg = Message.objects.filter(room=obj).order_by('-timestamp').first()
        if latest_msg:
            return latest_msg.text
        else:
            return None

    def get_opponent_email(self, obj):
        # 요청 사용자와 대화하는 상대방의 이메일 가져오기
        request_user_email = self.context['request'].query_params.get('email', None)
        if request_user_email == obj.shop_user.shop_user_email:
            return obj.visitor_user.visitor_user_email
        else:
            return obj.shop_user.shop_user_email

    def get_shop_user_email(self, obj):
        return obj.shop_user.shop_user_email

    def get_visitor_user_email(self, obj):
        return obj.visitor_user.visitor_user_email
