from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from accounts.models import User
from chat.models import ChatRoom, Message


# 각 클라이언트마다 '채널'을 보유하고 있음

class ChatConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        # 클라이언트가 웹소켓에 연결하려고 할 때 호출
        # url 경로에서 room_id를 추출하고 해당하는 방이 있다면 해당 그룹에 현재 채널을 추가하고 연결을 수락
        try:
            self.room_id = self.scope['url_route']['kwargs']['room_id']

            if not await self.check_room_exists(self.room_id):
                raise ValueError("채팅방이 존재하지 않습니다.")

            group_name = self.get_group_name(self.room_id)

            await self.channel_layer.group_add(group_name, self.channel_name)
            await self.accept()
        except ValueError as e:
            await self.send_json({'error': str(e)})
            await self.close()

    async def disconnect(self, close_code):
        # 클라이언트가 웹소켓 연결을 종료할 때 호출
        # 해당 그룹에서 클라이언트의 채널을 제거
        try:
            group_name = self.get_group_name(self.room_id)
            await self.channel_layer.group_discard(group_name, self.channel_name)
        except Exception as e:
            pass

    async def receive_json(self, content, **kwargs):
        # 클라이언트로부터 Json 메시지를 받았을 때 호출
        # 받은 메시지를 데이터베이스에 저장하고 동일한 그룹 내의 모든 채널(클라이언트)에 메시지를 전송
        try:
            message = content['message']
            sender_email = content['sender_email']
            room_id = content['room_id']


            sender, room = await self.get_user_and_chatroom(sender_email, room_id)


            # room_id 업데이트
            self.room_id = str(room.id)

            # 그룹 이름 가져오기
            group_name = self.get_group_name(self.room_id)

            # 수신된 메시지를 데이터베이스에 저장
            await self.save_message(room, sender, message)

            # 메시지를 전체 그룹에 전송
            await self.channel_layer.group_send(group_name, {
                'type': 'chat_message',
                'message': message,
                'sender_username': sender.username
            })

        except ValueError as e:
            await self.send_json({'error': str(e)})

    async def chat_message(self, event):
        # 그룹 내의 다른 클라이언트로부터 메시지를 받았을 때 호출
        # 받은 메시지를 현재 채널(클라이언트)에 전송한다
        try:
            message = event['message']
            sender_username = event['sender_username']

            await self.send_json({'message': message, 'sender_username': sender_username})
        except Exception as e:
            await self.send_json({'error': '메시지 전송 실패'})

    @staticmethod
    def get_group_name(room_id):
        return f'chat_room_{room_id}'

    # @database_sync_to_async
    # def get_or_create_room(self, shop_user_email, visitor_user_email):
    #     shop_user, _ = ShopUser.objects.get_or_create(shop_user_email=shop_user_email)
    #     visitor_user, _ = VisitorUser.objects.get_or_create(visitor_user_email=visitor_user_email)
    #
    #     # try:
    #     #     shop_user = User.objects.get(email=shop_user_email)
    #     # except User.DoesNotExist as e:
    #     #     raise ValueError("물건 주인의 이메일을 User에서 찾을 수 없습니다.")
    #     #
    #     # try:
    #     #     visitor_user = User.objects.get(email=visitor_user_email)
    #     # except User.DoesNotExist as e:
    #     #     raise ValueError("구매/대여 희망자의 이메일을 User에서 찾을 수 없습니다.")
    #
    #     # 두 이메일을 받고 ChatRoom을 생성
    #     room, created = ChatRoom.objects.get_or_create(
    #         shop_user=shop_user,
    #         visitor_user=visitor_user
    #     )
    #     return room


    @database_sync_to_async
    def get_user_and_chatroom(self, sender_email, room_id):
        sender = User.objects.get(email=sender_email)
        room = ChatRoom.objects.get(id=room_id)
        return sender, room


    @database_sync_to_async
    def save_message(self, room, sender, message_text):
        if not message_text:
            raise ValueError("메시지 텍스트가 필요합니다.")

        # 메시지를 생성하고 데이터베이스에 저장
        Message.objects.create(room=room, sender=sender, text=message_text)

    @database_sync_to_async
    def check_room_exists(self, room_id):
        return ChatRoom.objects.filter(id=room_id).exists()