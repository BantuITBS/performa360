from django import forms
from .models import UserCreationModel

class UserCreationForm(forms.ModelForm):
    class Meta:
        model = UserCreationModel
        fields = [
            'first_name', 
            'last_name', 
            'employee_email', 
            'phone_number', 
            'team_or_division', 
            'is_employee_active', 
            'reason_for_inactivity',
            'employee_status', 
            'employment_type', 
            'department', 
            'position',
            'company_code',
            'employee_name',
            'date_of_birth',
            'employee_gender',
            'reports_to',
            'employment_start_date',
        ]
        widgets = {
            'reason_for_inactivity': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control'})

    def clean(self):
        cleaned_data = super().clean()
        # Add additional validation logic here if needed
        return cleaned_data


class EmployeeCodeForm(forms.Form):
    employee_code = forms.CharField(
        max_length=10,
        required=True,
        widget=forms.TextInput(attrs={
            'id': 'employee_code',
            'placeholder': 'Enter your employee code',
            'required': True,
            'class': 'form-control'
        })
    )


