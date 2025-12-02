from rest_framework.generics import RetrieveAPIView
from rest_framework import permissions

from apps.main.models import Oferta
from apps.main.serializers import OfertaSerializer


class OfertaView(RetrieveAPIView):
    """
    Oferta ma'lumotlarini olish uchun API.
    Faqat active bo'lgan ofertani qaytaradi.
    """
    serializer_class = OfertaSerializer
    permission_classes = [permissions.AllowAny]  # Barcha foydalanuvchilar o'qishi mumkin
    
    def get_object(self):
        # Faqat active bo'lgan ofertani qaytaradi
        oferta = Oferta.objects.filter(is_active=True).first()
        if not oferta:
            from rest_framework.exceptions import NotFound
            raise NotFound("Not found")
        return oferta

