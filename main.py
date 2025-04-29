import json
import asyncio
import re
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command, CommandStart
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

from  config import TOKEN

bot = Bot(token=TOKEN)
dp = Dispatcher()

DATA_FILE = "users.json"

class UserForm(StatesGroup):
    ism = State()
    tel_nomer = State()
    yosh = State()
    qayerliki = State()
    ish_joyi = State()


def save_to_json(new_data: dict):
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as file:
            data = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        data = []

    data.append(new_data)

    with open(DATA_FILE, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)


async def send_help_message(message: types.Message, state_name: str):
    helps = {
        "ism": (
            " **Ism kiritish**:\n"
            "- To'liq ism va familiya (kamida 3 harf).\n"
            "- Faqat harflar va bo'sh joy.\n"
            "Misol: Sardorbek Xojimatov"
        ),
        "tel_nomer": (
            " **Telefon raqami kiritish**:\n"
            "- +998 bilan boshlansin, 9 raqam (12 belgi).\n"
            "- Bo'sh joy yoki chiziqcha yo'q.\n"
            "Misol: +998901234567"
        ),
        "yosh": (
            " **Yosh kiritish**:\n"
            "- Faqat raqam (1-150).\n"
            "- Harf yoki belgi kiritmang.\n"
            "Misol: 23"
        ),
        "qayerliki": (
            " **Qayerliki kiritish**:\n"
            "- Yashash joyingiz (kamida 5 harf).\n"
            "- Shahar, tuman yoki viloyat yozing.\n"
            "Misol: Toshkent shahri"
        ),
        "ish_joyi": (
            " **Ish joyi kiritish**:\n"
            "- Ish joyingiz yoki kasbingiz (kamida 3 harf).\n"
            "- Harflar va bo'sh joy.\n"
            "Misol: Dasturchi"
        )
    }
    await message.answer(helps.get(state_name, "Yordam: ma'lumotni to'g'ri kiriting!"))


def is_valid_name(name: str) -> bool:
    return bool(re.match(r"^[a-zA-Zа-яА-ЯёЁ\s]{3,}$", name.strip()))


def is_valid_phone(phone: str) -> bool:
    return bool(re.match(r"^\+998[0-9]{9}$", phone))


def is_valid_age(age: str) -> bool:
    return age.isdigit() and 1 <= int(age) <= 150


def is_valid_qayerliki(qayerliki: str) -> bool:
    return len(qayerliki.strip()) >= 5


def is_valid_ish_joyi(ish_joyi: str) -> bool:
    return bool(re.match(r"^[a-zA-Zа-яА-ЯёЁ\s]{3,}$", ish_joyi.strip()))


@dp.message(StateFilter(UserForm.ism), Command("help"))
@dp.message(StateFilter(UserForm.ism), lambda message: message.text.lower() == "help")
async def help_ism(message: types.Message):
    await send_help_message(message, "ism")


@dp.message(StateFilter(UserForm.tel_nomer), Command("help"))
@dp.message(StateFilter(UserForm.tel_nomer), lambda message: message.text.lower() == "help")
async def help_tel_nomer(message: types.Message):
    await send_help_message(message, "tel_nomer")


@dp.message(StateFilter(UserForm.yosh), Command("help"))
@dp.message(StateFilter(UserForm.yosh), lambda message: message.text.lower() == "help")
async def help_yosh(message: types.Message):
    await send_help_message(message, "yosh")


@dp.message(StateFilter(UserForm.qayerliki), Command("help"))
@dp.message(StateFilter(UserForm.qayerliki), lambda message: message.text.lower() == "help")
async def help_qayerliki(message: types.Message):
    await send_help_message(message, "qayerliki")


@dp.message(StateFilter(UserForm.ish_joyi), Command("help"))
@dp.message(StateFilter(UserForm.ish_joyi), lambda message: message.text.lower() == "help")
async def help_ish_joyi(message: types.Message):
    await send_help_message(message, "ish_joyi")


@dp.message(CommandStart())
async def cmd_start(message: types.Message, state: FSMContext):
    await message.answer(
        " Salom! .\n"
        " Ismingizni kiriting:"
    )
    await state.set_state(UserForm.ism)


@dp.message(Command("cancel"))
async def cmd_cancel(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer(
        " Jarayon bekor qilindi.\n"
        " Qayta boshlash uchun /start ni bosing."
    )


@dp.message(StateFilter(UserForm.ism))
async def process_ism(message: types.Message, state: FSMContext):
    if not is_valid_name(message.text):
        await send_help_message(message, "ism")
        return
    await state.update_data(ism=message.text.strip())
    await message.answer(" Telefon raqamingizni kiriting:")
    await state.set_state(UserForm.tel_nomer)


@dp.message(StateFilter(UserForm.tel_nomer))
async def process_tel(message: types.Message, state: FSMContext):
    if not is_valid_phone(message.text):
        await send_help_message(message, "tel_nomer")
        return
    await state.update_data(tel_nomer=message.text)
    await message.answer(" Yoshingizni kiriting:")
    await state.set_state(UserForm.yosh)


@dp.message(StateFilter(UserForm.yosh))
async def process_yosh(message: types.Message, state: FSMContext):
    if not is_valid_age(message.text):
        await send_help_message(message, "yosh")
        return
    await state.update_data(yosh=message.text)
    await message.answer(" Qayerlikisiz (yashash joyingiz):")
    await state.set_state(UserForm.qayerliki)


@dp.message(StateFilter(UserForm.qayerliki))
async def process_qayerliki(message: types.Message, state: FSMContext):
    if not is_valid_qayerliki(message.text):
        await send_help_message(message, "qayerliki")
        return
    await state.update_data(qayerliki=message.text.strip())
    await message.answer("💼 Ish joyingiz yoki kasbingiz:")
    await state.set_state(UserForm.ish_joyi)


@dp.message(StateFilter(UserForm.ish_joyi))
async def process_ish_joyi(message: types.Message, state: FSMContext):
    if not is_valid_ish_joyi(message.text):
        await send_help_message(message, "ish_joyi")
        return
    await state.update_data(ish_joyi=message.text.strip())
    data = await state.get_data()

    save_to_json(data)

    await message.answer(
        " Ma'lumotlaringiz saqlandi!\n"
        f" Ism: {data['ism']}\n"
        f" Telefon: {data['tel_nomer']}\n"
        f" Yosh: {data['yosh']}\n"
        f" Qayerliki: {data['qayerliki']}\n"
        f" Ish joyi: {data['ish_joyi']}\n\n"
        " Qayta ro'yxatdan o'tish uchun /start ni bosing."
    )

    await state.clear()


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
