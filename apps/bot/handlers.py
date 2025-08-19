import secrets
from asgiref.sync import sync_to_async

from aiogram import Router, types, F
from aiogram.filters import CommandStart, CommandObject
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from apps.user.models import PendingVerification
from django.core.exceptions import ObjectDoesNotExist
from django.core.cache import cache

router = Router()


@router.message(CommandStart(deep_link=True))
async def start_command(message: Message, command: CommandObject, state: FSMContext):
    args = command.args
    await state.set_data({"token": args})

    kb = types.ReplyKeyboardMarkup(keyboard=[
        [types.KeyboardButton(text="📱 Telfon raqamni yuborish", request_contact=True)]
    ], resize_keyboard=True)
    await message.answer("Botga xush kelibsiz. Iltmos telfon raqamingizni yuboring:", reply_markup=kb)


@router.message(F.contact)
async def get_contact(message: Message, state: FSMContext):
    data = await state.get_data()
    token = data.get("token")

    # if not token:
    #     await message.answer("Token topilmadi yoki seans eskirgan.")
    #     return

    phone = message.contact.phone_number.strip()

    try:
        pending = await sync_to_async(
        lambda: PendingVerification.objects.filter(uuid=token, phone=phone).first()
    )()
    except Exception as err:
        await message.answer("Xatolik sodir bo'ldi!")
        print("Xatolik:", str(err))
        return

    if not pending:
        await message.answer("Telfon raqam yoki token most kelmadi.")
        return

    
    cache_obj = cache.get(f"otp:{phone}")
    if cache_obj:
        await message.answer("Sizda faol otp kod bor!")
        return
    
    generate_code = str(secrets.randbelow(9000) + 1000)  
    cache.set(f"otp:{phone}", generate_code, 120)

    await message.answer("Tasdiqlash kodingiz: <b>{}</b>".format(generate_code), parse_mode="HTML")
    

    await state.clear()