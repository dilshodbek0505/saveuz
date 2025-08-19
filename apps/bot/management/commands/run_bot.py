import asyncio
from django.core.management.base import BaseCommand
from aiogram import Bot, Dispatcher
from django.conf import settings

from apps.bot.handlers import router

class Command(BaseCommand):
    help = "Aiogram 3 botni Django orqali polling rejimida ishga tushuradi"

    def handle(self, *args, **options):
        asyncio.run(self.run_bot())

    async def run_bot(self):
        bot = Bot(token=settings.TELEGRAM_BOT_TOKEN)
        dp = Dispatcher()
        dp.include_router(router)

        self.stdout.write(self.style.SUCCESS("Bot polling orqali ishga tushdi..."))
        await dp.start_polling(bot)
