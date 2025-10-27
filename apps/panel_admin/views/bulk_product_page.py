from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.db import transaction
from django.shortcuts import redirect
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView

from apps.main.models import Product
from apps.panel_admin.forms import ProductBulkFormSet


@method_decorator(staff_member_required, name="dispatch")
class BulkProductAdminPageView(TemplateView):
    template_name = "panel_admin/bulk_product_form.html"
    formset_prefix = "products"

    def get_formset(self, data=None, files=None):
        return ProductBulkFormSet(
            data=data,
            files=files,
            queryset=Product.objects.none(),
            prefix=self.formset_prefix,
        )

    def get(self, request, *args, **kwargs):
        formset = self.get_formset()
        return self.render_to_response(self.get_context_data(formset=formset))

    def post(self, request, *args, **kwargs):
        formset = self.get_formset(data=request.POST, files=request.FILES)

        if not formset.is_valid():
            messages.error(request, "Iltimos, kiritilgan ma'lumotlarni tekshiring.")
            return self.render_to_response(self.get_context_data(formset=formset))

        created = []
        with transaction.atomic():
            for form in formset.forms:
                if not form.has_changed():
                    continue
                if form.cleaned_data.get("id"):
                    continue
                created.append(form.save())

        if not created:
            messages.warning(request, "Yangi mahsulot qo'shilmadi.")
            return self.render_to_response(self.get_context_data(formset=self.get_formset()))

        messages.success(request, f"{len(created)} ta mahsulot muvaffaqiyatli yaratildi.")
        return redirect(request.path)

