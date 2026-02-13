from django import forms

from apps.main.models import Product, CommonProduct


class ProductAdminForm(forms.ModelForm):
    """Product admin uchun maxsus forma"""

    ADD_MODE_CHOICES = [
        ('common', 'Umumiy mahsulotlar bazasidan qo\'shish'),
        ('manual', 'Qo\'lda qo\'shish'),
    ]

    add_mode = forms.ChoiceField(
        choices=ADD_MODE_CHOICES,
        widget=forms.RadioSelect(attrs={'class': 'add-mode-selector'}),
        label='Qo\'shish usuli',
        required=False,
        initial='manual',
    )

    class Meta:
        model = Product
        fields = '__all__'
        widgets = {
            'common_product': forms.Select(attrs={
                'class': 'common-product-select',
                'data-placeholder': 'Umumiy bazadan mahsulot tanlang'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Делает ручные поля не обязательными на уровне формы
        manual_fields = [
            'name',
            'name_ru',
            'name_uz',
            'name_en',
            'description',
            'description_ru',
            'description_uz',
            'description_en',
            'category',
        ]
        for field in manual_fields:
            if field in self.fields:
                self.fields[field].required = False

        # Определяем режим на основе наличия common_product
        if self.instance and self.instance.pk:
            if self.instance.common_product_id:
                self.fields['add_mode'].initial = 'common'
                # Делаем поля ручного ввода readonly, если выбран common_product
                for field in manual_fields:
                    if field in self.fields and field != 'category':
                        self.fields[field].widget.attrs['readonly'] = True
                if 'category' in self.fields:
                    self.fields['category'].widget.attrs['readonly'] = True
            else:
                self.fields['add_mode'].initial = 'manual'
        else:
            self.fields['add_mode'].initial = 'manual'
        
        self.fields['common_product'].help_text = (
            'Umumiy bazadan mahsulot tanlang. Nomi, tavsif va kategoriya avtomatik olinadi.'
        )
        self.fields['name'].help_text = (
            'Umumiy bazadan mahsulot tanlanmasa, qo\'lda to\'ldiring.'
        )
        self.fields['description'].help_text = (
            'Umumiy bazadan mahsulot tanlanmasa, qo\'lda to\'ldiring.'
        )
        self.fields['category'].help_text = (
            'Umumiy bazadan mahsulot tanlanmasa, qo\'lda to\'ldiring.'
        )

    def clean(self):
        cleaned_data = super().clean()
        add_mode = cleaned_data.get('add_mode')
        common_product = cleaned_data.get('common_product')
        
        # Если add_mode не пришел, определяем по common_product
        if not add_mode:
            add_mode = 'common' if common_product else 'manual'
            cleaned_data['add_mode'] = add_mode

        # Если выбран продукт из общей базы, всегда считаем режим common
        if common_product and add_mode != 'common':
            add_mode = 'common'
            cleaned_data['add_mode'] = 'common'

        if add_mode == 'common':
            if not common_product:
                raise forms.ValidationError({
                    'common_product': 'Umumiy bazadan mahsulot tanlashingiz kerak.'
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
                'name': 'Qo\'lda qo\'shishda nomi talab qilinadi.',
                'name_ru': 'Qo\'lda qo\'shishda nomi (RU) talab qilinadi.',
                'name_uz': 'Qo\'lda qo\'shishda nomi (UZ) talab qilinadi.',
                'name_en': 'Qo\'lda qo\'shishda nomi (EN) talab qilinadi.',
                'description': 'Qo\'lda qo\'shishda tavsif talab qilinadi.',
                'description_ru': 'Qo\'lda qo\'shishda tavsif (RU) talab qilinadi.',
                'description_uz': 'Qo\'lda qo\'shishda tavsif (UZ) talab qilinadi.',
                'description_en': 'Qo\'lda qo\'shishda tavsif (EN) talab qilinadi.',
                'category': 'Qo\'lda qo\'shishda kategoriya talab qilinadi.',
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
