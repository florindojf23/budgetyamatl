from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from .models import *
from .forms import YearBudgetForm, DirectionForm, BudgetItemForm, ActivityForm
from django.db.models import Q
import xlsxwriter
from django.http import HttpResponse
from django.views import View
from django.http import JsonResponse


# ==============================
# YearBudget
# ==============================
@login_required
def YearBudgetList(request):
    objects = YearBudget.objects.all()
    context = {
        'title': "List Year Budgets",
        'page': "list",
        'objects': objects,
    }
    return render(request, 'budget/yearbudget_list.html', context)

@login_required
def YearBudgetAdd(request):
    if request.method == "POST":
        form = YearBudgetForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                instance = form.save(commit=False)
                # set remaining_amount same as total_amount
                instance.remaining_amount = instance.total_amount
                instance.save()
                messages.success(request, "Year Budget added successfully.")
                return redirect('yearbudget-list')
    else:
        form = YearBudgetForm()
    context = {
        'title': "Add Year Budget",
        'page': "form",
        'form': form,
    }
    return render(request, 'budget/form.html', context)

@login_required
def YearBudgetUpdate(request, pk):
    objects = get_object_or_404(YearBudget, pk=pk)
    if request.method == "POST":
        form = YearBudgetForm(request.POST, instance=objects)
        if form.is_valid():
            with transaction.atomic():
                instance = form.save(commit=False)
                # optionally update remaining_amount if you want
                # instance.remaining_amount = instance.total_amount
                instance.save()
                messages.success(request, "Year Budget updated successfully.")
                return redirect('yearbudget-list')
    else:
        form = YearBudgetForm(instance=objects)
    context = {
        'title': f"Update Year Budget {objects.year}",
        'page': "form",
        'form': form,
    }
    return render(request, 'budget/form.html', context)

@login_required
def YearBudgetDelete(request, pk):
    objects = get_object_or_404(YearBudget, pk=pk)
    if request.method == "POST":
        objects.delete()
        messages.success(request, "Year Budget deleted successfully.")
        return redirect('yearbudget-list')
    context = {
        'title': f"Delete Year Budget {objects.year}",
        'object': objects,
    }
    return render(request, 'budget/yearbudget_confirm_delete.html', context)


# Direction
@login_required
def DirectionList(request):
    objects = Direction.objects.all()
    context = {
        'title': "List Directions",
        'page': "list",
        'objects': objects,
    }
    return render(request, 'budget/direction_list.html', context)

def direction_list(request):
    directions = Direction.objects.all()  # Get all directions
    context = {
        'directions': directions,
        'title': 'Direction List',  # This will appear in base.html title
    }
    return render(request, 'main/base.html', context)  # We use base.html

@login_required
def DirectionAdd(request):
    if request.method == "POST":
        form = DirectionForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                instance = form.save(commit=False)
                instance.remaining_amount = instance.total_amount
                instance.save()
                messages.success(request, "Direction added successfully.")
                return redirect('direction-list')
    else:
        form = DirectionForm()
    context = {
        'title': "Add Direction",
        'page': "form",
        'form': form,
    }
    return render(request, 'budget/form.html', context)

@login_required
def DirectionUpdate(request, pk):
    objects = get_object_or_404(Direction, pk=pk)
    if request.method == "POST":
        form = DirectionForm(request.POST, instance=objects)
        if form.is_valid():
            with transaction.atomic():
                instance = form.save(commit=False)
                instance.save()
                messages.success(request, "Direction updated successfully.")
                return redirect('direction-list')
    else:
        form = DirectionForm(instance=objects)
    context = {
        'title': f"Update Direction {objects.name}",
        'page': "form",
        'form': form,
    }
    return render(request, 'budget/form.html', context)

@login_required
def DirectionDelete(request, pk):
    objects = get_object_or_404(Direction, pk=pk)
    if request.method == "POST":
        objects.delete()
        messages.success(request, "Direction deleted successfully.")
        return redirect('direction-list')
    context = {
        'title': f"Delete Direction {objects.name}",
        'object': objects,
    }
    return render(request, 'budget/direction_confirm_delete.html', context)


class DirectionServerSideJson(View):
    def get(self, request, *args, **kwargs):

        # DATATABLE PARAMETERS
        draw = int(request.GET.get('draw', 1))
        start = int(request.GET.get('start', 0))
        length = int(request.GET.get('length', 10))

        search_value = request.GET.get('search[value]', '').strip()

        order_column_index = request.GET.get('order[0][column]')
        order_direction = request.GET.get('order[0][dir]', 'asc')

        # COLUMN MAP
        column_map = {
            0: 'name',
            1: 'year_budget__year',
            2: 'total_amount',
            3: 'remaining_amount',
        }

        # BASE QUERYSET
        queryset = Direction.objects.select_related('year_budget').all()
        records_total = queryset.count()

        # GLOBAL SEARCH
        if search_value:
            search_filter = (
                Q(name__icontains=search_value) |
                Q(year_budget__year__icontains=search_value)
            )

            # numeric safe search
            if search_value.replace('.', '', 1).isdigit():
                search_filter |= (
                    Q(total_amount=search_value) |
                    Q(remaining_amount=search_value)
                )

            queryset = queryset.filter(search_filter)

        records_filtered = queryset.count()

        # ORDERING
        if order_column_index is not None:
            column_index = int(order_column_index)
            column_name = column_map.get(column_index, 'id')

            if order_direction == 'desc':
                column_name = f'-{column_name}'

            queryset = queryset.order_by(column_name)

        # PAGINATION
        queryset = queryset[start:start + length]

        # RESPONSE DATA
        data = []
        for item in queryset:
            data.append({
                'id': item.id,
                'name': item.name,
                'year_budget': item.year_budget.year if item.year_budget else '',
                'total_amount': float(item.total_amount),
                'remaining_amount': float(item.remaining_amount),
            })

        return JsonResponse({
            'draw': draw,
            'recordsTotal': records_total,
            'recordsFiltered': records_filtered,
            'data': data,
        })

# BudgetItem
@login_required
def BudgetItemList(request):
    objects = BudgetItem.objects.all()
    context = {
        'title': "List Budget Items",
        'page': "list",
        'objects': objects,
    }
    return render(request, 'budget/budget_list.html', context)

@login_required
def BudgetItemAdd(request):
    if request.method == "POST":
        form = BudgetItemForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                instance = form.save(commit=False)
                instance.remaining_amount = instance.initial_amount
                instance.save()
                messages.success(request, "Budget Item added successfully.")
                return redirect('budgetitem-list')
    else:
        form = BudgetItemForm()
    context = {
        'title': "Add Budget Item",
        'page': "form",
        'form': form,
    }
    return render(request, 'budget/form.html', context)

@login_required
def BudgetItemUpdate(request, pk):
    objects = get_object_or_404(BudgetItem, pk=pk)
    if request.method == "POST":
        form = BudgetItemForm(request.POST, instance=objects)
        if form.is_valid():
            with transaction.atomic():
                instance = form.save(commit=False)
                instance.save()
                messages.success(request, "Budget Item updated successfully.")
                return redirect('budgetitem-list')
    else:
        form = BudgetItemForm(instance=objects)
    context = {
        'title': f"Update Budget Item {objects.get_item_type_display()}",
        'page': "form",
        'form': form,
    }
    return render(request, 'budget/form.html', context)

@login_required
def BudgetItemDelete(request, pk):
    objects = get_object_or_404(BudgetItem, pk=pk)
    if request.method == "POST":
        objects.delete()
        messages.success(request, "Budget Item deleted successfully.")
        return redirect('budgetitem-list')
    context = {
        'title': f"Delete Budget Item {objects.get_item_type_display()}",
        'object': objects,
    }
    return render(request, 'budget/budgetitem_confirm_delete.html', context)

class BudgetItemServerSideJson(View):
    def get(self, request, *args, **kwargs):

        # DataTables parameters
        draw = int(request.GET.get('draw', 1))
        start = int(request.GET.get('start', 0))
        length = int(request.GET.get('length', 10))

        # Global search
        search_value = request.GET.get('search[value]', '').strip()

        # Ordering
        order_column_index = request.GET.get('order[0][column]')
        order_direction = request.GET.get('order[0][dir]', 'asc')

        # Map datatable column index → model field
        column_map = {
            0: 'direction__name',
            1: 'item_type',
            2: 'initial_amount',
            3: 'remaining_amount',
        }

        # Base queryset
        queryset = BudgetItem.objects.select_related('direction')

        records_total = queryset.count()

        # GLOBAL SEARCH
        if search_value:
            search_filter = (
                Q(direction__name__icontains=search_value) |
                Q(item_type__icontains=search_value)
            )

            # Numeric safe search for amounts
            if search_value.replace('.', '', 1).isdigit():
                search_filter |= (
                    Q(initial_amount=search_value) |
                    Q(remaining_amount=search_value)
                )

            queryset = queryset.filter(search_filter)

        records_filtered = queryset.count()

        # ORDERING
        if order_column_index is not None:
            column_index = int(order_column_index)
            column_name = column_map.get(column_index, 'id')

            if order_direction == 'desc':
                column_name = f'-{column_name}'

            queryset = queryset.order_by(column_name)

        # PAGINATION
        queryset = queryset[start:start + length]

        # RESPONSE DATA
        data = []
        for item in queryset:
            data.append({
                'id': item.id,
                'direction': item.direction.name if item.direction else '',
                'item_type': item.get_item_type_display(),
                'initial_amount': float(item.initial_amount),
                'remaining_amount': float(item.remaining_amount),
            })

        return JsonResponse({
            'draw': draw,
            'recordsTotal': records_total,
            'recordsFiltered': records_filtered,
            'data': data,
        })

# Activity
@login_required
def ActivityList(request):
    objects = Activity.objects.all()
    context = {
        'title': "List Activities",
        'page': "list",
        'objects': objects,
    }
    return render(request, 'budget/activity_list.html', context)

@login_required
def ActivityAdd(request):
    if request.method == "POST":
        form = ActivityForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                instance = form.save()
                messages.success(request, "Activity added successfully.")
                return redirect('activity-list')
    else:
        form = ActivityForm()
    context = {
        'title': "Add Activity",
        'page': "form",
        'form': form,
    }
    return render(request, 'budget/form.html', context)

@login_required
def ActivityUpdate(request, pk):
    objects = get_object_or_404(Activity, pk=pk)
    if request.method == "POST":
        form = ActivityForm(request.POST, instance=objects)
        if form.is_valid():
            with transaction.atomic():
                instance = form.save()
                messages.success(request, "Activity updated successfully.")
                return redirect('activity-list')
    else:
        form = ActivityForm(instance=objects)
    context = {
        'title': f"Update Activity {objects.name}",
        'page': "form",
        'form': form,
    }
    return render(request, 'budget/form.html', context)

@login_required
def ActivityDelete(request, pk):
    objects = get_object_or_404(Activity, pk=pk)
    if request.method == "POST":
        objects.delete()
        messages.success(request, "Activity deleted successfully.")
        return redirect('activity-list')
    context = {
        'title': f"Delete Activity {objects.name}",
        'object': objects,
    }
    return render(request, 'budget/activity_confirm_delete.html', context)


class BudgetActivityServerSideJson(View):
    def get(self, request, *args, **kwargs):

        # DataTables parameters
        draw = int(request.GET.get('draw', 1))
        start = int(request.GET.get('start', 0))
        length = int(request.GET.get('length', 10))

        # Global search
        search_value = request.GET.get('search[value]', '').strip()

        # Ordering
        order_column_index = request.GET.get('order[0][column]')
        order_direction = request.GET.get('order[0][dir]', 'asc')

        column_map = {
            0: 'name',
            1: 'place',
            2: 'amount',
            3: 'date',
            4: 'budget_item__name',
        }

        # Base queryset
        queryset = Activity.objects.select_related(
            'budget_item',
            'budget_item__direction'
        )

        records_total = queryset.count()

        # GLOBAL SEARCH
        if search_value:
            queryset = queryset.filter(
                Q(name__icontains=search_value) |
                Q(place__icontains=search_value) |
                Q(budget_item__name__icontains=search_value)
            )

            # Amount search (numeric safe)
            if search_value.replace('.', '', 1).isdigit():
                queryset = queryset | Activity.objects.filter(amount=search_value)

        records_filtered = queryset.count()

        # ORDERING
        if order_column_index is not None:
            column_index = int(order_column_index)
            column_name = column_map.get(column_index, 'id')

            if order_direction == 'desc':
                column_name = f'-{column_name}'

            queryset = queryset.order_by(column_name)

        # PAGINATION
        queryset = queryset[start:start + length]

        # RESPONSE DATA
        data = []
        for item in queryset:
            data.append({
                'id': item.id, 
                'name': item.name,
                'place': item.place,
                'amount': float(item.amount),  # Decimal → float
                'date': item.date.strftime('%Y-%m-%d') if item.date else '',
                'budget_item': str(item.budget_item) if item.budget_item else ''
            })

        return JsonResponse({
            'draw': draw,
            'recordsTotal': records_total,
            'recordsFiltered': records_filtered,
            'data': data,
        })


def activity_excel(request):
    # Create HTTP response with Excel content
    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = 'attachment; filename=ListaAtividade.xlsx'

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
        'Item',
        'Atividade',
        'Fatin',
        'Montante',
        'Data',
    ]

    for col, header in enumerate(headers):
        worksheet.write(0, col, header, header_format)

    # Write data rows
    row = 1
    activity = Activity.objects.select_related(
        'budget_item__direction'
    )

    for doc in activity:
        worksheet.write(row, 0, doc.budget_item.direction.name if doc.budget_item else '')
        worksheet.write(row, 1, doc.name)
        worksheet.write(row, 2, doc.place)
        worksheet.write(row, 3, doc.amount)
        worksheet.write(row, 4, doc.date.strftime('%Y-%m-%d'))
        row += 1

    # Auto column width
    worksheet.set_column('A:I', 20)

    workbook.close()
    return response
