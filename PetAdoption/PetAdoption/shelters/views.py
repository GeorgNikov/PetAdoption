# from django.contrib.auth.mixins import LoginRequiredMixin
# from django.shortcuts import get_object_or_404
# from django.urls import reverse_lazy
# from django.views.generic import DetailView
#
# from PetAdoption.accounts.models import ShelterProfile
# from PetAdoption.pets.models import Pet
#
#
#
# # Create your views here.
# class ShelterProfileView(LoginRequiredMixin, DetailView):
#     model = ShelterProfile
#     template_name = 'shelters/shelter_profile.html'
#     context_object_name = 'shelter_profile'
#     login_url = reverse_lazy('index')
#
#
#     def get_object(self):
#         # Returns the ShelterProfile instance for the logged-in user
#         return get_object_or_404(ShelterProfile, user=self.request.user)
#
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context['shelter_profile'] = self.get_object()  # This is the profile of the logged-in user
#         pets = Pet.objects.filter(owner=self.request.user).order_by('-created_at')
#         context['pets'] = pets
#         print(context['pets'])
#         return context
#
#     def success_url(self):
#         return reverse_lazy('shelter profile view', kwargs={'pk': self.request.user.pk})