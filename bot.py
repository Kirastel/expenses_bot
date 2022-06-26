import logging
import os

import aiohttp
from aiogram import Bot, Dispatcher, executor, types

import config
import exceptions
import expenses
from categories import Categories
from middlewares import AccessMiddleware


logging.basicConfig(level=logging.INFO)

API_TOKEN = config.API_TOKEN
ACCESS_ID = config.ACCESS_ID

bot = Bot(API_TOKEN)
dp = Dispatcher(bot)
dp.middleware.setup(AccessMiddleware(ACCESS_ID))


@dp.message_handler(commands=['start', 'help'])
async def send_welcome(message: types.Message):
    await message.answer(
        'Bot for accounting finance.\n'
        'All expenses are kept in BYN.\n'
        'In order to add an expense point,\n enter the category and the amount you spent\n Ex: 100 taxis'
        'Today\'s statistics: /today\n'
        'For the current month: /month\n'
        'Last contributed expenses: /expenses\n'
        'Categories of expenses: /categories')


@dp.message_handler(lambda message: message.text.startswith('/del'))
async def del_expense(message: types.Message):
    row_id = int(message.text[4:])
    expenses.delete_expense(row_id)
    answer_message = "deleted"
    await message.answer(answer_message)


@dp.message_handler(commands=['categories'])
async def categories_list(message: types.Message):
    categories = Categories().get_all_categories()
    answer_message = "Categories of expenses:\n\n* " +\
            ("\n* ".join([c.name+' ('+", ".join(c.aliases)+')' for c in categories]))
    await message.answer(answer_message)


@dp.message_handler(commands=['today'])
async def today_statistics(message: types.Message):
    answer_message = expenses.get_today_statistics()
    await message.answer(answer_message, parse_mode=types.ParseMode.HTML)


@dp.message_handler(commands=['month'])
async def month_statistics(message: types.Message):
    answer_message = expenses.get_month_statistics()
    await message.answer(answer_message, parse_mode=types.ParseMode.HTML)


@dp.message_handler(commands=['expenses'])
async def list_expenses(message: types.Message):
    last_expenses = expenses.last()
    if not last_expenses:
        await message.answer("No expenses")
        return

    last_expenses_rows = [
        f"<b>{expense.amount}</b> BYN. on {expense.category_name} — click "
        f"/del{expense.id} for delete"
        for expense in last_expenses]
    answer_message = "Last saved expenses:\n\n* " + "\n\n* "\
            .join(last_expenses_rows)
    await message.answer(answer_message, parse_mode=types.ParseMode.HTML)


@dp.message_handler()
async def add_expense(message: types.Message):
    try:
        expense = expenses.add_expense(message.text)
    except exceptions.NotCorrectMessage as e:
        await message.answer(str(e))
        return
    answer_message = (
        f"Added expenses <b>{expense.amount}</b> BYN on {expense.category_name}.\n\n"
        f"{expenses.get_today_statistics()}")
    await message.answer(answer_message, parse_mode=types.ParseMode.HTML)


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)