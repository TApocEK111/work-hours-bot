from aiogram import F, Router
from aiogram.filters.command import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message

from api.keyboards import clockinout_reply_keyboard
from application.exceptions import InvalidUserNameError, UserAlreadyExistsError
from application.services.user import UserService
from infrastructure.env import EnvVars, get_env

router = Router(name="basic")


class Registration(StatesGroup):
    waiting_for_password = State()


@router.message(Command("start"))
async def cmd_start(message: Message, user_service: UserService, state: FSMContext):
    if message.from_user is None:
        await message.answer("Oops. Seem's that for some reason I can't see user info.")
        return

    user = await user_service.get_by_id(message.from_user.id)

    if user:
        await message.answer("Welcome back, master.", reply_markup=clockinout_reply_keyboard())
    else:
        await message.answer(
            "Hi! You are new here. Enter the passphrase for registration or reset with /cancel."
        )
        await state.set_state(Registration.waiting_for_password)


@router.message(Registration.waiting_for_password, ~F.text.startswith("/"))
async def process_password(
    message: Message, state: FSMContext, user_service: UserService
):
    if not message.from_user:
        await message.answer(
            "For some reason I can't see the user info, so I can't register you."
        )
        await state.clear()
        return
    correct_password = get_env(EnvVars.REGISTRATION_PASSWORD)
    if message.text == correct_password:
        try:
            is_created = await user_service.create(
                message.from_user.id, message.from_user.full_name
            )
            if is_created:
                await message.answer("You are successfully registered. Welcome!")
            await state.clear()
        except UserAlreadyExistsError:
            await message.answer(
                "Somehow you've attempted to register a registered user."
            )
        except InvalidUserNameError:
            await message.answer("Your name breaks me ;(")
    else:
        await message.answer("Incorrect passphrase, try again.")


@router.message(Command("cancel"))
async def cmd_cancel(message: Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state == Registration.waiting_for_password.state:
        await state.clear()
        await message.answer("Registration canceled.\nUse /start to try again.")
    else:
        await message.answer("Nothing to cancel.")


@router.message(Command("help"))
async def cmd_help(message: Message):
    await message.answer(
        "You can use these commands:\n\n"
        "/start - check authorization status and update keyboard\n"
        "/help - show this message\n\n"
        "<b>Main Usage</b>\n"
        "/clockin - use when you enter the work\n"
        "/clockout - use when you leave the work\n\n"
        "<b>View Hours</b>\n"
        "/today - see working hours today\n"
        "/thisweek - see working hours this week (can be across months)\n"
        "/thismonth - see working hours this month (from 1st)\n",
        parse_mode="HTML",
    )
