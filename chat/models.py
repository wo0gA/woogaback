from django.db import models

# Create your models here.
class ChatRoom(models.Model):
    shop_user = models.ForeignKey('accounts.User', on_delete=models.CASCADE, related_name='shop_user')
    visitor_user = models.ForeignKey('accounts.User', on_delete=models.CASCADE, related_name='visitor_user')
    timestamp = models.DateTimeField(auto_now_add=True)
    class Meta:
        unique_together = ('shop_user', 'visitor_user')

class Message(models.Model):
    room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name='messages')
    sender_email = models.EmailField()
    text = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)