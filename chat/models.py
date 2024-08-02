from django.db import models

# Create your models here.
class ChatRoom(models.Model):
    # shop_user = models.ForeignKey(ShopUser, on_delete=models.CASCADE)
    # visitor_user = models.ForeignKey(VisitorUser, on_delete=models.CASCADE)
    shop_user = models.ForeignKey('accounts.User', on_delete=models.CASCADE, related_name='shop_user')
    visitor_user = models.ForeignKey('accounts.User', on_delete=models.CASCADE, related_name='visitor_user')
    product = models.ForeignKey('products.Product', on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    class Meta:
        unique_together = ('shop_user', 'visitor_user', 'product')

class Message(models.Model):
    room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name='messages')
    # sender_email = models.EmailField()
    sender = models.ForeignKey('accounts.User', on_delete=models.CASCADE, related_name='sender')
    text = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)