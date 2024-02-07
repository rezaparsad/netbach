from django import forms
from ckeditor_uploader.widgets import CKEditorUploadingWidget
from .models import Category


class CreateServerCloudFrom(forms.Form):
    slug = forms.CharField(max_length=20)
    os = forms.CharField(max_length=30)
    location = forms.CharField(max_length=50)


class InlineTokenForm(forms.ModelForm):
    key = forms.CharField(widget=forms.Textarea)


class CategoryAdminFrom(forms.ModelForm):
    name = forms.CharField(widget=forms.TextInput(attrs={"style": "width: 80%"}))
    content = forms.CharField(widget=CKEditorUploadingWidget())
    title = forms.CharField(widget=forms.TextInput(attrs={"style": "width: 80%"}))
    description = forms.CharField(widget=forms.Textarea)
    slug = forms.SlugField(widget=forms.TextInput(attrs={"style": "width: 80%"}))
