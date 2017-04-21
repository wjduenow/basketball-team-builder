from django import forms

from .models import Player

class PlayerForm(forms.ModelForm):

    class Meta:
        model = Player
        fields = ('first_name', 'last_name','nick_name', 'referred_by', 'status', 'size', 'position', 'ball_handler')