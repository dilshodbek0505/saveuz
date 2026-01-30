from modeltranslation.translator import register, TranslationOptions
from apps.main.models import CommonProduct, Product, Market, Banner, Category


@register(Product)
class ProductTranslationOptions(TranslationOptions):
    fields = ("name", "description")

@register(CommonProduct)
class CommonProductTranslationOptions(TranslationOptions):
    fields = ("name", "description")

@register(Market)
class MarketTranslationOptions(TranslationOptions):
    fields = ("name", "description")

@register(Banner)
class BannerTranslationOptions(TranslationOptions):
    fields = ("image", )

@register(Category)
class CategoryTranslationOptions(TranslationOptions):
    fields = ("name", )