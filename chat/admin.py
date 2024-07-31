from django.contrib import admin

from chat.models import *

# Register your models here.
admin.site.register(ShopUser)
admin.site.register(VisitorUser)
admin.site.register(ChatRoom)
admin.site.register(Message)