from django import forms


class CreateServerCloudFrom(forms.Form):
    slug = forms.CharField(max_length=20)
    os = forms.CharField(max_length=30)
    location = forms.CharField(max_length=50)


class InlineTokenForm(forms.ModelForm):
    key = forms.CharField(widget=forms.Textarea)
