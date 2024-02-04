from django import forms

from .models import PackTicket


class ProfileForm(forms.Form):
    first_name = forms.CharField(required=False)
    last_name = forms.CharField(required=False)
    email = forms.EmailField(max_length=100, required=False)
    state = forms.CharField(max_length=30, strip=False, required=False)
    city = forms.CharField(max_length=40, strip=False, required=False)
    id_card = forms.CharField(strip=False, required=False)
    zip_code = forms.CharField(strip=False, required=False)
    address = forms.CharField(strip=False, required=False)


class PackTicketForm(forms.ModelForm):
    title = forms.CharField(widget=forms.TextInput(attrs={"style": "width: 80%"}))


class TicketForm(forms.ModelForm):
    content = forms.CharField(widget=forms.TextInput(attrs={"style": "width: 80%"}))


class InlineTicketForm(forms.ModelForm):
    content = forms.CharField(widget=forms.Textarea)


class EditTicketForm(forms.Form):
    content = forms.CharField(max_length=1024, widget=forms.Textarea)


class CreateTicketForm(forms.Form):

    def __init__(self, *args, **kwargs):
        categorys = [i for i in PackTicket.CHOICES_CATEGORY]
        categorys.append(('', '---------'))
        categorys = categorys[::-1]
        REPLY_CHOICES = tuple(categorys)
        super().__init__(*args, **kwargs)
        self.fields['category'].choices = REPLY_CHOICES
    
    category = forms.ChoiceField()
    title = forms.CharField(max_length=100)
    content = forms.CharField(max_length=1024, widget=forms.Textarea)