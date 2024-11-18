from django import forms
from PetAdoption.pets.models import Pet


class PetBaseForm(forms.ModelForm):
    owner = forms.HiddenInput()
    slug = forms.HiddenInput()

    class Meta:
        model = Pet
        fields = ('name', 'type', 'breed', 'age', 'description', 'image')


class AddPetForm(PetBaseForm):
    pass

class EditPetForm(PetBaseForm):
    type = forms.HiddenInput()

    class Meta(PetBaseForm.Meta):
        fields = ('name', 'breed', 'age', 'description', 'image')


    # name = forms.CharField(
    #     max_length=30,
    #     label='Name',
    #     widget=forms.TextInput(
    #         attrs={
    #             'placeholder': 'Name',
    #         }
    #     )
    # )
    #
    # bread = forms.CharField(
    #     max_length=30,
    #     label='Breed',
    #     widget=forms.TextInput(
    #         attrs={
    #             'placeholder': 'Breed'
    #         }
    #     )
    # )
    #
    # age = forms.IntegerField(
    #     label='Age',
    #     widget=forms.NumberInput(
    #         attrs={
    #             'placeholder': 'Age'
    #         }
    #     )
    # )
    #
    # image = forms.ImageField(
    #     label='Image',
    #     widget=forms.FileInput(
    #         attrs={
    #             'placeholder': 'Image'
    #         }
    #     )
    # )