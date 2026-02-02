from django import forms
from django.utils.translation import gettext_lazy as _

from apps.main.models import Product, CommonProduct


class ProductAdminForm(forms.ModelForm):
    """Кастомная форма для админки Product с выбором режима добавления"""
    
    ADD_MODE_CHOICES = [
        ('common', _('Добавить из общей базы продуктов')),
        ('manual', _('Добавить вручную')),
    ]
    
    add_mode = forms.ChoiceField(
        choices=ADD_MODE_CHOICES,
        widget=forms.RadioSelect(attrs={'class': 'add-mode-selector'}),
        label=_('Способ добавления'),
        required=True,
        initial='manual',
    )

    class Meta:
        model = Product
        fields = '__all__'
        widgets = {
            'common_product': forms.Select(attrs={
                'class': 'common-product-select',
                'data-placeholder': _('Выберите продукт из общей базы')
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Определяем режим на основе наличия common_product
        if self.instance and self.instance.pk:
            if self.instance.common_product_id:
                self.fields['add_mode'].initial = 'common'
                # Делаем поля ручного ввода readonly, если выбран common_product
                self.fields['name'].widget.attrs['readonly'] = True
                self.fields['description'].widget.attrs['readonly'] = True
                self.fields['category'].widget.attrs['readonly'] = True
            else:
                self.fields['add_mode'].initial = 'manual'
        else:
            self.fields['add_mode'].initial = 'manual'
        
        # Настраиваем help_text для полей
        self.fields['common_product'].help_text = _(
            'Выберите продукт из общей базы. Название, описание и категория будут взяты автоматически.'
        )
        self.fields['name'].help_text = _(
            'Заполните вручную, если не выбран продукт из общей базы.'
        )
        self.fields['description'].help_text = _(
            'Заполните вручную, если не выбран продукт из общей базы.'
        )
        self.fields['category'].help_text = _(
            'Заполните вручную, если не выбран продукт из общей базы.'
        )

    def clean(self):
        cleaned_data = super().clean()
        add_mode = cleaned_data.get('add_mode')
        common_product = cleaned_data.get('common_product')
        
        if add_mode == 'common':
            if not common_product:
                raise forms.ValidationError({
                    'common_product': _('Необходимо выбрать продукт из общей базы.')
                })
            # Очищаем поля, которые будут взяты из common_product
            cleaned_data['name'] = None
            cleaned_data['name_ru'] = None
            cleaned_data['name_uz'] = None
            cleaned_data['name_en'] = None
            cleaned_data['description'] = None
            cleaned_data['description_ru'] = None
            cleaned_data['description_uz'] = None
            cleaned_data['description_en'] = None
            cleaned_data['category'] = common_product.category if common_product else None
        elif add_mode == 'manual':
            required_fields = {
                'name': _('Название обязательно при ручном добавлении.'),
                'name_ru': _('Название (RU) обязательно при ручном добавлении.'),
                'name_uz': _('Название (UZ) обязательно при ручном добавлении.'),
                'name_en': _('Название (EN) обязательно при ручном добавлении.'),
                'description': _('Описание обязательно при ручном добавлении.'),
                'description_ru': _('Описание (RU) обязательно при ручном добавлении.'),
                'description_uz': _('Описание (UZ) обязательно при ручном добавлении.'),
                'description_en': _('Описание (EN) обязательно при ручном добавлении.'),
                'category': _('Категория обязательна при ручном добавлении.'),
            }
            errors = {}
            for field, message in required_fields.items():
                if not cleaned_data.get(field):
                    errors[field] = message
            if errors:
                raise forms.ValidationError(errors)
            cleaned_data['common_product'] = None
        
        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)
        
        # Если выбран common_product, очищаем ручные поля
        if instance.common_product:
            instance.name = None
            instance.name_ru = None
            instance.name_uz = None
            instance.name_en = None
            instance.description = None
            instance.description_ru = None
            instance.description_uz = None
            instance.description_en = None
            instance.category = instance.common_product.category
        
        if commit:
            instance.save()
        
        return instance
