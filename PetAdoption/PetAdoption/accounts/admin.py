from django.contrib import admin
from django.contrib.auth import get_user_model

from PetAdoption.accounts.forms import CustomUserChangeForm, CustomUserCreationForm
from PetAdoption.accounts.models import UserProfile, ShelterProfile

UserModel = get_user_model()

@admin.register(UserModel)
class UserAdmin(admin.ModelAdmin):
    model = UserModel
    form = CustomUserChangeForm
    add_form = CustomUserCreationForm

    readonly_fields = ('last_login',)

    list_filter = ('is_staff', 'is_active')
    list_display = ('username', 'email', 'is_staff', 'is_active')
    ordering = ('pk',)

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2')}
        ),
    )

    fieldsets = (
        ('Credentials', {'fields': ('username', 'email', 'password')}),
        ('Permissions', {'fields': ('is_staff', 'groups', 'is_active', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login',)}),
    )

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    model = UserProfile
    readonly_fields = ('created_at', 'updated_at')


@admin.register(ShelterProfile)
class ShelterProfileAdmin(admin.ModelAdmin):
    model = ShelterProfile
    readonly_fields = ('created_at', 'updated_at', 'slug')
