from ckeditor_uploader.widgets import CKEditorUploadingWidget
from django import forms

from .models import Page


class PageAdminFrom(forms.ModelForm):
    name = forms.CharField(widget=forms.TextInput(attrs={"style": "width: 80%"}))
    content = forms.CharField(widget=CKEditorUploadingWidget())
    title = forms.CharField(widget=forms.TextInput(attrs={"style": "width: 80%"}))
    description = forms.CharField(widget=forms.Textarea)

    class Meta:
        model = Page
        fields = '__all__'
