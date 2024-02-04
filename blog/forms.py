from ckeditor_uploader.widgets import CKEditorUploadingWidget
from django import forms

from .models import Blog, Category


class BlogAdminFrom(forms.ModelForm):
    name = forms.CharField(widget=forms.TextInput(attrs={"style": "width: 80%"}))
    content = forms.CharField(widget=CKEditorUploadingWidget())
    slug = forms.SlugField(required=False, widget=forms.TextInput(attrs={"style": "width: 80%"}))
    Blog._meta.get_field('slug')._unique = False
    title = forms.CharField(widget=forms.TextInput(attrs={"style": "width: 80%"}))
    description = forms.CharField(widget=forms.Textarea)

    class Meta:
        model = Blog
        fields = '__all__'


class CategoryAdminFrom(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        categorys = [(i.pk, i.name) for i in Category.objects.filter(is_active=True)]
        categorys.append(('', '---------'))
        categorys = categorys[::-1]
        REPLY_CHOICES = tuple(categorys)
        super().__init__(*args, **kwargs)
        self.fields['reply_id'].choices = REPLY_CHOICES

    name = forms.CharField(widget=forms.TextInput(attrs={"style": "width: 80%"}))
    content = forms.CharField(widget=CKEditorUploadingWidget())
    reply_id = forms.ChoiceField(required=False)
    title = forms.CharField(widget=forms.TextInput(attrs={"style": "width: 80%"}))
    description = forms.CharField(widget=forms.Textarea)
    slug = forms.SlugField(widget=forms.TextInput(attrs={"style": "width: 80%"}))

    class Meta:
        model = Category
        fields = '__all__'
