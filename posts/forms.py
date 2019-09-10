from django import forms
from tinymce import TinyMCE
from .models import Post, Comment


class TinyMCEWidget(TinyMCE):
    def use_required_attribute(self, *args):
        return False

class EmailPostForm(forms.Form):
    name = forms.CharField(max_length=25)
    email = forms.EmailField()
    to = forms.EmailField()
    comments = forms.CharField(required=False, widget=forms.Textarea)

class SearchForm(forms.Form):
    query = forms.CharField()


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('name', 'email', 'body')
        labels = {
            'body': 'Comment'
        }
