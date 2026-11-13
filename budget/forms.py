from django import forms
from .models import *
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column, Submit, Div,HTML


class YearBudgetForm(forms.ModelForm):
    class Meta:
        model = YearBudget
        fields = ['year', 'total_amount']

class DirectionForm(forms.ModelForm):
    class Meta:
        model = Direction
        fields = ['name', 'year_budget', 'total_amount']
        

class BudgetItemForm(forms.ModelForm):

    direction = forms.ModelChoiceField(
        queryset=None,
        label='Direksaun',
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    item_type = forms.ChoiceField(
        choices=BudgetItem.ITEM_CHOICES,
        label='Tipu Item',
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    initial_amount = forms.DecimalField(
        label='Montante Inicial',
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )

    remaining_amount = forms.DecimalField(
        label='Montante Restante',
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'readonly': 'readonly'
        })
    )

    class Meta:
        model = BudgetItem
        fields = [
            'direction',
            'item_type',
            'initial_amount',
            'remaining_amount'
        ]

    def __init__(self, *args, **kwargs):
        from .models import Direction
        super().__init__(*args, **kwargs)

        # Load queryset here to avoid circular import
        self.fields['direction'].queryset = Direction.objects.all()

        # If creating new → hide remaining_amount
        if not self.instance.pk:
            self.fields['remaining_amount'].widget = forms.HiddenInput()

        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_class = 'row mt-4'

        self.helper.layout = Layout(
            Column('direction', css_class='col-md-6 my-3'),
            Column('item_type', css_class='col-md-6 my-3'),
            Column('initial_amount', css_class='col-md-6 my-3'),
            Column('remaining_amount', css_class='col-md-6 my-3'),

            HTML("""
                <br>
                <div class='d-flex justify-content-end py-6 px-9 gap-2'>
                    <a href='#' class='btn btn-warning' onclick=self.history.back()>
                        <i class='bi bi-arrow-left-square'></i> Kansela
                    </a>
                    <button type='submit' class='btn btn-primary'>
                        <i class='bi bi-save'></i> Save
                    </button>
                </div>
            """)
        )

class DateInput(forms.DateInput):
    input_type = 'date'


class ActivityForm(forms.ModelForm):
    date = forms.DateField(
        label='Data Atividade',
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )

    budget_item = forms.ModelChoiceField(
        queryset=BudgetItem.objects.all(),
        label='Item Orsamentu',
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    class Meta:
        model = Activity
        fields = ['budget_item', 'name', 'place', 'amount', 'date']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'place': forms.TextInput(attrs={'class': 'form-control'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_class = 'row mt-4'

        self.helper.layout = Layout(
            Column('budget_item', css_class='col-md-6 my-3'),
            Column('name', css_class='col-md-6 my-3'),
            Column('place', css_class='col-md-6 my-3'),
            Column('amount', css_class='col-md-6 my-3'),
            Column('date', css_class='col-md-4 my-3'),

            HTML("""
                <br>
                <div class='d-flex justify-content-end py-6 px-9 gap-2'>
                    <a href='#' class='btn btn-warning' onclick=self.history.back()>
                        <i class='bi bi-arrow-left-square'></i> Kansela
                    </a>
                    <button type='submit' class='btn btn-primary'>
                        <i class='bi bi-save'></i> Save
                    </button>
                </div>
            """)
        )