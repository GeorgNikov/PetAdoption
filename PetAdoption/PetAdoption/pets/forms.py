from django import forms
from PetAdoption.pets.models import Pet, AdoptionRequest
from cloudinary.forms import CloudinaryFileField

from .choices import PetChoices


class PetBaseForm(forms.ModelForm):
    owner = forms.HiddenInput()
    slug = forms.HiddenInput()
    image = CloudinaryFileField()

    class Meta:
        model = Pet
        fields = ('name', 'type', 'breed', 'age', 'gender', 'size', 'description', 'image')


class AddPetForm(PetBaseForm):
    description = forms.CharField(widget=forms.Textarea, required=False)
    image = CloudinaryFileField(required=False)

    class Meta(PetBaseForm.Meta):
        fields = ('name', 'type', 'breed', 'age', 'gender', 'size', 'description', 'image')



class EditPetForm(PetBaseForm):
    type = forms.HiddenInput()
    description = forms.CharField(widget=forms.Textarea, required=False)
    image = CloudinaryFileField(required=False)

    class Meta(PetBaseForm.Meta):
        fields = ('name', 'breed', 'age', 'gender', 'size', 'description', 'image')



class AdoptionRequestForm(forms.ModelForm):
    class Meta:
        model = AdoptionRequest
        fields = ['message']  # Allow the adopter to write a message


from django import forms
from .models import Pet


class PetFilterForm(forms.Form):
    # Filter by pet type
    type = forms.ChoiceField(
        choices=[('', 'All Types')] + [(choice[0], choice[1]) for choice in PetChoices.choices],
        required=False
    )

    # # Filter by species
    # species = forms.ChoiceField(choices=[('', 'All Species')] + [(sp, sp) for sp in Pet.SPECIES_CHOICES],
    #                             required=False)

    # Filter by age
    age = forms.ChoiceField(choices=[('', 'All Ages')] + [(str(i), str(i) + ' years') for i in range(1, 21)],
                            required=False)

    # Filter by gender
    gender = forms.ChoiceField(choices=[('', 'All Genders')] + [('M', 'Male'), ('F', 'Female')], required=False)

    # Filter by size
    size = forms.ChoiceField(
        choices=[('', 'All Sizes')] + [('Small', 'Small'), ('Medium', 'Medium'), ('Large', 'Large')], required=False)

