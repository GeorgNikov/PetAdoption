from django.contrib import admin

from PetAdoption.pets.models import Pet, AdoptionRequest


# Register your models here.
@admin.register(Pet)
class PetAdmin(admin.ModelAdmin):
    list_display = ('name', 'type', 'breed', 'age', 'gender', 'size', 'description', 'image')
    list_filter = ('type', 'breed', 'age', 'gender', 'size')
    search_fields = ('name', 'breed')
    list_per_page = 10

    fieldsets = (
        ('Pet Details', {
            'fields': ('name', 'type', 'breed', 'age', 'gender', 'size', 'description', 'image')
        }),
    )

    readonly_fields = ('created_at', 'updated_at')


@admin.register(AdoptionRequest)
class AdoptionRequestAdmin(admin.ModelAdmin):
    list_display = ('pet', 'adopter', 'status', 'created_at', 'updated_at')
    list_filter = ('status', 'created_at', 'updated_at')
    search_fields = ('pet__name', 'adopter__username')
    list_per_page = 10