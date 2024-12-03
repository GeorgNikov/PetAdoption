from django.contrib import admin

from PetAdoption.core.models import ShelterRating


# Register your models here.
@admin.register(ShelterRating)
class ShelterRatingAdmin(admin.ModelAdmin):
    list_display = ('shelter', 'rating', 'created_at')
    list_filter = ('rating',)
    search_fields = ('shelter__organization_name', 'shelter__user__username')
    list_per_page = 10