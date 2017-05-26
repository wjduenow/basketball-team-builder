from django import forms

from .models import Player, GymSlot

class PlayerForm(forms.ModelForm):

    class Meta:
        model = Player
        fields = ('first_name', 'last_name','nick_name', 'referred_by', 'status', 'size', 'position', 'ball_handler')



class GymSlotForm(forms.ModelForm):

    class Meta:
        model = GymSlot
        fields = ('group', 'name', 'status','location', 'start_date', 'end_date', 'start_time', 'end_time', 'day_of_week', 'black_out_dates')


