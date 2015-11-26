from django.contrib import admin
from django import forms
from django.forms import Textarea
from genequery.searcher.models import IdMap, ModuleDescription, GQModule


class IdMapAdmin(admin.ModelAdmin):
    list_display = ('species', 'entrez_id', 'refseq_id', 'symbol_id')


class ModuleDescriptionAdmin(admin.ModelAdmin):
    list_display = ('series', 'title')


class ModuleGenesForm(forms.ModelForm):
    class Meta:
        model = GQModule
        widgets = {'entrez_ids': Textarea(attrs={'cols': 150, 'rows': 10})}


class ModuleGenesAdmin(admin.ModelAdmin):
    form = ModuleGenesForm

admin.site.register(IdMap, IdMapAdmin)
admin.site.register(ModuleDescription, ModuleDescriptionAdmin)
admin.site.register(GQModule, ModuleGenesAdmin)