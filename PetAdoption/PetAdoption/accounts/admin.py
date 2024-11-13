from django.contrib import admin
from django.contrib.auth import get_user_model

from PetAdoption.accounts.forms import CustomUserChangeForm, CustomUserCreationForm

UserModel = get_user_model()
@admin.register(UserModel)
class UserAdmin(admin.ModelAdmin):
    form = CustomUserChangeForm
    add_form = CustomUserCreationForm

    readonly_fields = ('last_login',)

    list_filter = ('is_staff', 'is_active')
    list_display = ('username', 'email', 'is_staff', 'is_active')

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'is_staff', 'is_active')}
        ),
    )

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Permissions', {'fields': ('is_staff', 'is_active')}),
        ('Important dates', {'fields': ('last_login',)}),
    )