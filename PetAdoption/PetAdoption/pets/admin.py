from django.contrib import admin

from PetAdoption.pets.models import Pet, AdoptionRequest


class AgeRangeFilter(admin.SimpleListFilter):
    title = 'age range'
    parameter_name = 'age_range'

    def lookups(self, request, model_admin):
        """
            Defines the options for the filter.
        """
        return (
            ('<12', '0 - 12 months'),
            ('12-24', '12 - 24 months'),
            ('24-48', '24 - 48 months'),
            ('48+', '48+ months'),
        )

    def queryset(self, request, queryset):
        """
            Filters the queryset based on the selected age range.
        """
        if self.value() == '<12':
            return queryset.filter(age__lt=12)
        if self.value() == '12-24':
            return queryset.filter(age__gte=12, age__lte=24)
        if self.value() == '24-48':
            return queryset.filter(age__gte=24, age__lte=48)
        if self.value() == '48+':
            return queryset.filter(age__gte=48)
        return queryset


# Register your models here.
@admin.register(Pet)
class PetAdmin(admin.ModelAdmin):
    list_display = ('name', 'type', 'breed', 'age', 'gender', 'size')
    list_filter = ('type', 'gender', 'size', AgeRangeFilter)
    search_fields = ('name', 'age', 'type', 'gender', 'size')
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