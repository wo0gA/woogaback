from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import User

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('username', 'email', 'provider', 'level', 'point', 'manner_score', 'profile')

class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = User
        fields = ('username', 'email', 'provider', 'level', 'point', 'manner_score', 'profile')

class CustomUserAdmin(BaseUserAdmin):
    form = CustomUserChangeForm
    add_form = CustomUserCreationForm

    # Custom fieldsets
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('email', 'provider', 'level', 'point', 'manner_score', 'profile')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'user_permissions')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'provider', 'level', 'point', 'manner_score', 'profile'),
        }),
    )
    list_display = ('username', 'email', 'is_staff', 'level', 'point', 'manner_score')
    search_fields = ('username', 'email')
    ordering = ('username',)

    filter_horizontal = ()

    # Readonly fields
    readonly_fields = ('level', 'point', 'manner_score')

admin.site.register(User, CustomUserAdmin)
