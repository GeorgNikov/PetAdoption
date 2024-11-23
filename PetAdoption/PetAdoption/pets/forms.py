from django import forms
from PetAdoption.pets.models import Pet, AdoptionRequest
from cloudinary.forms import CloudinaryFileField


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
