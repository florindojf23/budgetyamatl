from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import *
from documents.models import *
from documents.forms import *
from custom.utils import *
from custom.models import Core

# Create your views here.
# @login_required
# def ConfigDash(request):
#     objects = Core.objects.get(is_active=True)
#     if request.method == 'POST':
#         name = request.POST.get('name')
#         about = request.POST.get('about')
#         sigla = request.POST.get('sigla')
#         address = request.POST.get('address')
#         phone = request.POST.get('phone')
#         objects.name = name
#         objects.sigla = sigla
#         objects.enderesu = address
#         objects.nu_kontaktu = phone
#         objects.about = about
#         objects.save()
#         messages.success(request, f'Dadus Atualizadu ho Susesu!')
#         return redirect('config-dash')

#     context = {
#         'title': "Core Configuration",
#         'owner_active':'active',
#         'page':'Owner',
#         'objects':objects,
#     }
#     return render(request,'config_pages/owner.html',context)
@login_required
def ConfigDash(request):
    objects = Core.objects.filter(is_active=True).first()

    if request.method == 'POST' and objects:
        objects.name = request.POST.get('name')
        objects.about = request.POST.get('about')
        objects.sigla = request.POST.get('sigla')
        objects.enderesu = request.POST.get('address')
        objects.nu_kontaktu = request.POST.get('phone')
        objects.save()
        messages.success(request, 'Dadus Atualizadu ho Susesu!')
        return redirect('config-dash')

    context = {
        'title': "Core Configuration",
        'owner_active': 'active',
        'page': 'Owner',
        'objects': objects,
    }
    return render(request, 'config_pages/owner.html', context)

@login_required
def ConfigDocType(request):
    objects = DocsType.objects.all()
    context = {
        'title': "Tipu Dokumentu",
        'doctype_active':'active',
        'page':'Tipu Dokumentu',
        'objects':objects,
    }
    return render(request,'config_pages/docs.html',context)

@login_required
def ConfigDocCat(request):
    objects = DocsCategory.objects.all()
    context = {
        'title': "Kategoria Dokumentu",
        'doccat_active':'active',
        'page':'Kategoria Dokumentu',
        'objects':objects,
    }
    return render(request,'config_pages/docs.html',context)

@login_required
def ConfigEntity(request):
    objects = Entity.objects.all()
    context = {
        'title': "Entidade",
        'entity_active':'active',
        'page':'Entidade',
        'objects':objects,
    }
    return render(request,'config_pages/entity.html',context)

@login_required
def ConfigAddEntity(request):
    if request.method == "POST":
        name = request.POST.get("entity")   # matches name="entity" in template
        sigla = request.POST.get("sigla")   # matches name="sigla" in template
        Entity.objects.create(
            name=name,
            sigla=sigla,
            user_created=request.user
        )
        return redirect("config-entity")  # redirect to your table page
    return render(request, "config.html", {"page": "Entidade"})

@login_required
def ConfigEditEntity(request, pk):
    entity = Entity.objects.get(pk=pk)
    if request.method == "POST":
        entity.name = request.POST.get("name")
        entity.sigla = request.POST.get("sigla")
        entity.save()
        return redirect("config-entity")

    return render(request, "config_pages/entity_edit.html", {"entity": entity, "page": "Edit Entity"})

@login_required
def ConfigDeleteEntity(request, pk):
    entity = Entity.objects.get(pk=pk)
    entity.delete()
    return redirect("config-entity")

@login_required
def SubConfigEntity(request):
    objects = SubEntity.objects.select_related('entity')
    entities = Entity.objects.filter(is_active=True)

    context = {
        'title': "Sub Entidade",
        'sub_entity_active': 'active',
        'page': 'Sub Entidade',
        'objects': objects,
        'entities': entities,   
    }
    return render(request, 'config_pages/subentity.html', context)


@login_required
def ConfigAddSubEntity(request):
    if request.method == "POST":
        entity_id = request.POST.get("entity")
        name = request.POST.get("name")
        sigla = request.POST.get("sigla")

        SubEntity.objects.create(
            entity_id=entity_id,   # ✅ correct ForeignKey save
            name=name,
            sigla=sigla,
            user_created=request.user
        )
        return redirect("config-sub-entity")

    return redirect("config-sub-entity")

@login_required
def ConfigEditSubEntity(request, pk):
    subentity = SubEntity.objects.get(pk=pk)
    entities = Entity.objects.filter(is_active=True)

    if request.method == "POST":
        subentity.entity_id = request.POST.get("entity")
        subentity.name = request.POST.get("name")
        subentity.sigla = request.POST.get("sigla")
        subentity.save()

        return redirect("config-sub-entity")

    context = {
        "subentity": subentity,
        "entities": entities,
        "page": "Edit Sub Entidade",
    }
    return render(request, "config_pages/subentity_edit.html", context)


@login_required
def ConfigEmployee(request):
    objects = Employee.objects.select_related('subentity')
    subentities = SubEntity.objects.filter(is_active=True)

    context = {
        'title': "Funcionariu",
        'funcionariu_active': 'active',
        'page': 'Funcionariu',
        'objects': objects,
        'subentities': subentities,   # 🔥 REQUIRED
    }
    return render(request, 'config_pages/funcionariu.html', context)


@login_required
def ConfigAddEmployee(request):
    if request.method == "POST":
        subentity_id = request.POST.get("subentity")
        name = request.POST.get("name")
        sex = request.POST.get("sex")
        dob = request.POST.get("dob")
        image = request.FILES.get("image")

        Employee.objects.create(
            subentity_id=subentity_id,   # ✅ correct FK save
            name=name,
            sex=sex,
            dob=dob,
            image=image,
            user_created=request.user
        )
        return redirect("config-funcionariu")

    return redirect("config-funcionariu")


@login_required
def ConfigEditEmployee(request, pk):
    employee = Employee.objects.get(pk=pk)
    subentities = SubEntity.objects.filter(is_active=True)

    if request.method == "POST":
        employee.name = request.POST.get("name")
        employee.subentity_id = request.POST.get("subentity")
        employee.sex = request.POST.get("sex")
        employee.dob = request.POST.get("dob")

        if request.FILES.get("image"):
            employee.image = request.FILES.get("image")

        employee.save()
        return redirect("config-funcionariu")

    context = {
        "employee": employee,
        "subentities": subentities,
        "page": "Edit Funcionariu",
    }
    return render(request, "config_pages/funcionariu_edit.html", context)


@login_required
def ConfigAddDocType(request):
    if request.method == 'POST':
        docType = request.POST.get('docType')
        if docType:
            newid = getjustnewid(DocsCategory)
            new_hashid = hash_md5(str(newid))
            DocsType.objects.create(name=docType,hashed=new_hashid,user_created=request.user)
            messages.success(request, f'Dadus Tipu Dokumentu Rejistu ho Susesu!')
            return redirect('config-doc-types')

@login_required
def ConfigEditDocsType(request, pk):
    doc_type = DocsType.objects.get(pk=pk)
    if request.method == "POST":
        doc_type.name = request.POST.get("name")
        doc_type.save()
        return redirect("config-doc-types")

    return render(request, "config_pages/docs_type_edit.html", {"doc_type": doc_type, "page": "Edit Docs Type"})

@login_required
def ConfigDeleteDocsType(request, pk):
    doc_type = DocsType.objects.get(pk=pk)
    doc_type.delete()
    return redirect("config-doc-types")


@login_required
def ConfigAddDocCategory(request):
    if request.method == 'POST':
        docType = request.POST.get('docType')
        if docType:
            newid = getjustnewid(DocsCategory)
            new_hashid = hash_md5(str(newid))
            DocsCategory.objects.create(name=docType,hashed=new_hashid,user_created=request.user)
            messages.success(request, f'Dadus Kategoria Dokumentu Rejistu ho Susesu!')
            return redirect('config-doc-cat')

@login_required
def ConfigEditDocsCategory(request, pk):
    doc_cat = DocsCategory.objects.get(pk=pk)
    if request.method == "POST":
        doc_cat.name = request.POST.get("name")
        doc_cat.save()
        return redirect("config-doc-cat")

    return render(request, "config_pages/docs_category_edit.html", {"doc_cat": doc_cat, "page": "Edit Docs Category"})

@login_required
def ConfigDeleteDocsCategory(request, pk):
    doc_cat = DocsCategory.objects.get(pk=pk)
    doc_cat.delete()
    return redirect("config-doc-cat")

@login_required
def ConfigPage(request):
    # Always get the first (and only) Core object
    obj = Core.objects.first()

    if request.method == 'POST':
        # Update text fields
        obj.name = request.POST.get('name')
        obj.about = request.POST.get('about')
        obj.sigla = request.POST.get('sigla')
        obj.enderesu = request.POST.get('address')
        obj.nu_kontaktu = request.POST.get('phone')
        obj.save()

        messages.success(request, "Dadus Atualiza ho Susesu!")
        return redirect('config-dash')

    return render(request, 'config_pages/owner.html', {'objects': obj})


# 2️⃣ Separate view to update the image
@login_required
def ConfigUpdateOwnerImage(request):
    if request.method == 'POST':
        updatedImage = request.FILES.get('updatedImage')

        # Get the first Core object
        obj = Core.objects.first()

        if updatedImage and obj:
            obj.logo = updatedImage
            obj.save()
            messages.success(request, 'Dadus Imajen Atualiza ho Susesu!')

        return redirect('config-dash')

    return redirect('config-dash')
