from django.contrib import admin
from django.contrib.auth import get_user_model

from PetAdoption.accounts.forms import CustomUserCreationForm, \
    CustomUserChangeForm
from PetAdoption.accounts.models import UserProfile, ShelterProfile
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _

UserModel = get_user_model()

@admin.register(UserModel)
class UserAdmin(BaseUserAdmin):
    """
        Admin configuration for the User model.
    """
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = UserModel
    list_per_page = 10

    # Fields to display in the list view
    list_display = ('username', 'email', 'type_user', 'is_staff', 'is_active')
    list_filter = ('is_staff', 'is_active', 'type_user')
    ordering = ('pk',)

    # For adding a new user
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'type_user')}
        ),
    )

    # For editing an existing user
    fieldsets = (
        (_('Credentials'), {'fields': ('username', 'email', 'password')}),
        (_('Profile'), {'fields': ('type_user',)}),
        (_('Permissions'), {'fields': ('is_staff', 'is_active', 'groups', 'user_permissions')}),
        (_('Important dates'), {'fields': ('last_login',)}),
    )

    readonly_fields = ('last_login',)

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    """
        Admin configuration for the UserProfile model.
    """
    model = UserProfile
    readonly_fields = ('created_at', 'updated_at')
    list_display = ('user', 'phone_number', 'completed', 'user__is_active', 'created_at')
    search_fields = ('user__username', 'user__email', 'phone_number')
    list_filter = ('created_at', 'updated_at')

    def has_add_permission(self, request):
        """
            Prevent adding new UserProfiles manually in the admin. Signal already handles this
        """
        return False


@admin.register(ShelterProfile)
class ShelterProfileAdmin(admin.ModelAdmin):
    """
        Admin configuration for the ShelterProfile model.
    """
    model = ShelterProfile
    readonly_fields = ('created_at', 'updated_at', 'slug')
    list_display = ('display_name', 'user', 'created_at', 'slug')
    search_fields = ('organization_name', 'user__username', 'user__email', 'slug')
    list_filter = ('created_at', 'updated_at')

    def display_name(self, obj):
        """
            Return the organization name if available; otherwise, return the associated user's username.
        """
        return obj.organization_name if obj.organization_name else obj.user.username

    display_name.short_description = 'Organization Name or Username'  # Label for the admin column
    display_name.admin_order_field = 'organization_name'  # Allows sorting by organization_name

    def has_add_permission(self, request):
        """
            Prevent adding new UserProfiles manually in the admin.. Signal already handles this
        """
        return False
