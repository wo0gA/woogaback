from django.contrib import admin
from .models import *
from mptt.admin import DraggableMPTTAdmin

class CategoryAdmin(DraggableMPTTAdmin):
    list_display = (
        'tree_actions',
        'indented_title',
        'sort',
    )

admin.site.register(Category, CategoryAdmin)
admin.site.register(Product)
admin.site.register(Tag)
admin.site.register(Review)