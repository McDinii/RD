from django.contrib import admin
from django.utils.html import format_html
from django.contrib.admin import actions
from django.contrib import messages
from .models import Node, Address, Product, Employee, Contact
from mptt.admin import MPTTModelAdmin
from core.tasks import clear_debt_async
admin.site.register(Node, MPTTModelAdmin)

admin.site.register(Address)
admin.site.register(Product)
admin.site.register(Employee)
admin.site.register(Contact)


class NodeAdmin(admin.ModelAdmin):
    list_display = ['name', 'type','level','parent_link', 'debt']
    list_filter = ['contacts__address__city']
    actions = ['clear_debt']

    def parent_link(self, obj):
        parent = obj.parent
        if parent is not None:
            return format_html('<a href="{}">{}</a>', f"{parent.id}", parent)
        else:
            return '-'
    parent_link.short_description = 'Поставщик'

    def clear_debt(modeladmin, request, queryset):
        if queryset.count() > 20:
            clear_debt_async.delay(list(queryset.values_list('id', flat=True)))
            messages.success(request, 'Задолженность перед поставщиком будет очищена асинхронно.')
        else:
            for node in queryset:
                node.debt = 0
                node.save()
            messages.success(request, 'Задолженность перед поставщиком успешно очищена.')
    clear_debt.short_description = 'Очистить задолженность у выбранных объектов'

    def get_email_copy_button(self, obj):
        return format_html(
            '<button class="copy-email-btn" data-email="{}" style="color:white; background: linear-gradient(135deg,  rgb(252, 59, 91), rgb(92, 110, 243),rgb(253, 154, 64));">Копировать почту</button>',
            obj.contacts.email
        )
    get_email_copy_button.short_description = 'Копировать почту'
    get_email_copy_button.allow_tags = True

    def get_list_display(self, request):
        list_display = super().get_list_display(request)
        return list_display + ['get_email_copy_button']

    class Media:
        js = ('js/copy_email.js', )

admin.site.unregister(Node)
admin.site.register(Node, NodeAdmin)

