from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import *
from .forms import *
from django.db import transaction
from custom.utils import *
from django.http import JsonResponse
from django.views import View
from django.db.models import Q
import xlsxwriter
from django.http import HttpResponse

# Create your views here.
@login_required
def ArchivalDash(request):
	objects = Documents.objects.all()
	lista_categoria = DocsCategory.objects.all()
	context = {
		'title':"Dadus Arkivu",
		'page':"Dash",
		'objects':objects,
		'lista_categoria':lista_categoria,
	}
	return render(request,'documents/dash.html',context)

@login_required
def ArchivalAdd(request):
	if request.method == "POST":
		form = DocumentsForm(request.POST, request.FILES)
		if form.is_valid():
			with transaction.atomic():
				instance = form.save(commit=False)
				newid = getjustnewid(Documents)
				new_hashid = hash_md5(str(newid))
				instance.hashed = new_hashid
				instance.user_created = request.user
				instance.save() 
				messages.success(request, f'Dadus Arkivu rejista ona ho Susesu.')
				return redirect('ArchivalDash')
	else:
		form = DocumentsForm()
	context = {
		'title':"Rejistu Arkivu",
		'page':"form",
		'form':form,
	}
	return render(request,'documents/form.html',context)

@login_required
def ArchivalUpdate(request,hashid):
	objects = get_object_or_404(Documents,hashed=hashid)
	if request.method == "POST":
		form = DocumentsForm(request.POST, request.FILES,instance=objects)
		if form.is_valid():
			with transaction.atomic():
				instance = form.save(commit=False)
				instance.save() 
				messages.success(request, f'Dadus Arkivu altera ona ho Susesu.')
				return redirect('ArchivalDash')
	else:
		form = DocumentsForm(instance=objects)
	context = {
		'title':f"Altera Arkivu ho Numeru {objects.doc_number}",
		'page':"form",
		'form':form,
	}
	return render(request,'documents/form.html',context)

@login_required
def ArchivalDetail(request,hashid):
	request.session['previous_url'] = request.META.get('HTTP_REFERER', None)
	objects = get_object_or_404(Documents,hashed=hashid)
	context = {
		'title':f"Detallu Arkivu ho Numeru {objects.doc_number}",
		'page':"detail",
		'objects':objects,
	}
	return render(request,'documents/detail.html',context)
	
#table server side
# class DocumentsServerSideJson(View):
#     def get(self, request, *args, **kwargs):
#         # DataTables parameters
#         draw = int(request.GET.get('draw', 1))
#         start = int(request.GET.get('start', 0))
#         length = int(request.GET.get('length', 10))
#         search_kategoria = request.GET.get('search_kategoria', '')
#         search_tipu = request.GET.get('search_tipu', '')

#         # Base queryset (OPTIMIZED)
#         queryset = Documents.objects.select_related(
#             'employee',
#             'entity',
#             'category',
#             'doc_type'
#         )

#         # Filters
#         if search_kategoria:
#             queryset = queryset.filter(category__name__icontains=search_kategoria)

#         if search_tipu:
#             queryset = queryset.filter(doc_type__name__icontains=search_tipu)

#         total_records = queryset.count()

#         # Pagination
#         queryset = queryset[start:start + length]

#         # Data output (Employee + Entity added)
#         data = [
#             {
#                 'doc_number': item.doc_number,
#                 'naran': item.name,

#                 'employee': item.employee.name if item.employee else '',
#                 'entity': item.entity.name if item.entity else '',

#                 'kategoria': item.category.name if item.category else '',
#                 'tipu': item.doc_type.name if item.doc_type else '',
#                 'doc_date': item.doc_date.strftime("%Y-%m-%d") if item.doc_date else '',
#                 'hashed': item.hashed,
#             }
#             for item in queryset
#         ]

#         return JsonResponse({
#             'draw': draw,
#             'recordsTotal': total_records,
#             'recordsFiltered': total_records,
#             'data': data,
#         })

class DocumentsServerSideJson(View):
    def get(self, request, *args, **kwargs):

        # DataTables parameters
        draw = int(request.GET.get('draw', 1))
        start = int(request.GET.get('start', 0))
        length = int(request.GET.get('length', 10))

        # 🔍 Global search (DataTables default)
        search_value = request.GET.get('search[value]', '').strip()

        # Custom dropdown filters
        search_kategoria = request.GET.get('search_kategoria', '')
        search_tipu = request.GET.get('search_tipu', '')

        # Base queryset (optimized)
        queryset = Documents.objects.select_related(
            'employee',
            'entity',
            'category',
            'doc_type'
        )

        records_total = queryset.count()

        # 🔍 GLOBAL SEARCH
        if search_value:
            queryset = queryset.filter(
                Q(doc_number__icontains=search_value) |
                Q(name__icontains=search_value) |
                Q(employee__name__icontains=search_value) |
                Q(entity__name__icontains=search_value)
            )

        # Dropdown filters
        if search_kategoria:
            queryset = queryset.filter(category__name=search_kategoria)

        if search_tipu:
            queryset = queryset.filter(doc_type__name=search_tipu)

        records_filtered = queryset.count()

        # Pagination
        queryset = queryset[start:start + length]

        # Response data
        data = []
        for item in queryset:
            data.append({
                'doc_number': item.doc_number,
                'naran': item.name,
                'employee': item.employee.name if item.employee else '',
                'entity': item.entity.name if item.entity else '',
                'kategoria': item.category.name if item.category else '',
                'tipu': item.doc_type.name if item.doc_type else '',
                'doc_date': item.doc_date.strftime('%Y-%m-%d') if item.doc_date else '',
                'hashed': item.hashed,
            })

        return JsonResponse({
            'draw': draw,
            'recordsTotal': records_total,
            'recordsFiltered': records_filtered,
            'data': data,
        })

def export_documents_excel(request):
    # Create HTTP response with Excel content
    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = 'attachment; filename=documents.xlsx'

    # Create workbook and worksheet
    workbook = xlsxwriter.Workbook(response, {'in_memory': True})
    worksheet = workbook.add_worksheet('Documents')

    # Header style
    header_format = workbook.add_format({
        'bold': True,
        'border': 1,
        'align': 'center'
    })

    # Write header row
    headers = [
        'Funcionariu',
        'Entidade',
        'Karegoria',
        'Tipo Dokumentu',
        'Naran Dokumentu',
        'Numeru Dokumentu',
        'Data',
        'User',
        'Date Input'
    ]

    for col, header in enumerate(headers):
        worksheet.write(0, col, header, header_format)

    # Write data rows
    row = 1
    documents = Documents.objects.select_related(
        'employee', 'entity', 'category', 'doc_type', 'user_created'
    )

    for doc in documents:
        worksheet.write(row, 0, doc.employee.name if doc.employee else '')
        worksheet.write(row, 1, doc.entity.name if doc.entity else '')
        worksheet.write(row, 2, doc.category.name if doc.category else '')
        worksheet.write(row, 3, doc.doc_type.name if doc.doc_type else '')
        worksheet.write(row, 4, doc.name)
        worksheet.write(row, 5, doc.doc_number)
        worksheet.write(row, 6, doc.doc_date.strftime('%Y-%m-%d'))
        worksheet.write(row, 7, doc.user_created.username if doc.user_created else '')
        worksheet.write(row, 8, doc.date_created.strftime('%Y-%m-%d %H:%M') if doc.date_created else '')
        row += 1

    # Auto column width
    worksheet.set_column('A:I', 20)

    workbook.close()
    return response