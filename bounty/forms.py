from django import forms
from django.core.exceptions import ValidationError
from django.db.models import Q

from bounty import models


class BountyAdminForm(forms.ModelForm):
    model = models.Bounty

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data['start_date']
        end_date = cleaned_data['end_date']

        if start_date >= end_date:
            raise ValidationError('The Start date must be less than the end date.')

        if models.Bounty.objects.filter(
            Q(start_date__range=[start_date, end_date]) |
            Q(end_date__range=[start_date, end_date])
        ).exists():
            raise ValidationError('A Bounty event is already scheduled within this time range.')

        return cleaned_data
