from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column, Submit, Div,HTML

from documents.models import *

class DateInput(forms.DateInput):
    input_type = 'date'

class DocumentsForm(forms.ModelForm):
    doc_date = forms.DateField(label='Data Dokumentu', widget=DateInput())
    doc_type = forms.ModelChoiceField(
        queryset=DocsType.objects.all(),
        widget=forms.Select(attrs={'class': 'form-select '})
    )
    category = forms.ModelChoiceField(
        queryset=DocsCategory.objects.all(),
        widget=forms.Select(attrs={'class': 'form-select '})
    )
    filename = forms.FileField(label='Escolha Dokumentu',widget=forms.ClearableFileInput(attrs={'class':'form-control'}))
    class Meta:
        model = Documents
        fields = ['name','doc_number','doc_date','employee','entity','filename','doc_type','category']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_class = 'row mt-4'
        self.helper.layout = Layout(
                Column('doc_number', css_class='col-md-6 my-3'),
                Column('name', css_class='col-md-6 my-3'),
                Column('doc_type', css_class='col-md-4 my-3'),
                Column('employee', css_class='col-md-3 my-3'),
                Column('entity', css_class='col-md-4 my-3'),
                Column('category', css_class='col-md-4 my-3'),
                Column('doc_date', css_class='col-md-4 my-3'),
                Column('filename', css_class='col-md-10 my-3'),
                HTML(""" <br><div class='d-flex justify-content-end py-6 px-9 gap-2'>
                            <a href='#' class='btn btn-warning' onclick=self.history.back()><i class='bi bi-arrow-left-square'></i> Kansela</a>
                            <button type='submit' class='btn btn-primary'><i class='bi bi-save'></i> Save</button>
                        </div> """)
        )

