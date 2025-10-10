from django import forms
from django.contrib import admin, messages
from django.forms import modelformset_factory
from django.http import HttpResponseRedirect
from django.template.response import TemplateResponse
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from import_export.admin import ImportExportModelAdmin

from apps.main.models import Product
from apps.product.formats import ImageAwareXLSX
from apps.product.resources import ProductResource


class BulkProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = "__all__"


@admin.register(Product)
class ProductAdmin(ImportExportModelAdmin):
    resource_class = ProductResource
    formats = [ImageAwareXLSX]
    list_display = ("id", "name", "market")
    list_display_links = ("id", "name")
    search_fields = ("name", "market__name")
    readonly_fields = ("discount_value", "discount_price", "discount_type")
    bulk_formset_extra = 10

    def _restrict_market_queryset(self, formset, request):
        if request.user.is_staff and not request.user.is_superuser:
            allowed_markets = request.user.markets.all()
            for form in formset.forms:
                market_field = form.fields.get("market")
                if market_field is not None:
                    market_field.queryset = allowed_markets

    def add_view(self, request, form_url="", extra_context=None):
        if request.GET.get("_single") == "1":
            return super().add_view(request, form_url, extra_context)

        BulkFormSet = modelformset_factory(
            Product,
            form=BulkProductForm,
            extra=self.bulk_formset_extra,
            can_delete=False,
        )

        if request.method == "POST":
            formset = BulkFormSet(
                request.POST,
                request.FILES,
                queryset=Product.objects.none(),
            )
            self._restrict_market_queryset(formset, request)
            if formset.is_valid():
                created_objects = []
                for form in formset.forms:
                    if not form.has_changed():
                        continue
                    obj = form.save(commit=False)
                    self.save_model(request, obj, form, change=False)
                    form.save_m2m()
                    self.save_related(request, form, [], change=False)
                    created_objects.append(obj)
                    self.log_addition(
                        request,
                        obj,
                        self.construct_change_message(request, form, []),
                    )

                if created_objects:
                    self.message_user(
                        request,
                        _("Successfully added %(count)d products.")
                        % {"count": len(created_objects)},
                        level=messages.SUCCESS,
                    )
                    changelist_url = reverse(
                        f"admin:{self.model._meta.app_label}_{self.model._meta.model_name}_changelist",
                        current_app=self.admin_site.name,
                    )
                    return HttpResponseRedirect(changelist_url)

                self.message_user(
                    request,
                    _("No products were created. Please fill at least one form."),
                    level=messages.WARNING,
                )
        else:
            formset = BulkFormSet(queryset=Product.objects.none())
            self._restrict_market_queryset(formset, request)

        resolved_form_url = form_url or request.get_full_path()
        has_file_field = formset.is_multipart()
        errors = formset.total_error_count()

        context = {
            **self.admin_site.each_context(request),
            "opts": self.model._meta,
            "formset": formset,
            "media": formset.media,
            "add": True,
            "change": False,
            "is_popup": False,
            "save_as": False,
            "has_view_permission": self.has_view_permission(request),
            "has_add_permission": True,
            "has_change_permission": False,
            "has_editable_inline_admin_formsets": False,
            "title": _("Add products"),
            "form_url": resolved_form_url,
            "has_file_field": has_file_field,
            "errors": errors,
        }
        if extra_context:
            context.update(extra_context)

        request.current_app = self.admin_site.name
        return TemplateResponse(
            request,
            "admin/main/product/bulk_add.html",
            context,
        )

    def get_queryset(self, request):
        user = request.user
        qs = super().get_queryset(request)
        qs = qs.select_related("market")

        if user.is_staff and not user.is_superuser:
            markets = user.markets.all()
            qs = qs.filter(market__in=markets)

        return qs

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if (
            db_field.name == "market"
            and request.user.is_staff
            and not request.user.is_superuser
        ):
            kwargs["queryset"] = request.user.markets.all()
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
