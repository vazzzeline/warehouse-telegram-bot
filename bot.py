import os
from datetime import datetime
import telebot
from telebot import types
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

TOKEN = "ВАШ_ТОКЕН_ОТ_BOTFATHER"
DATA_FILE = "warehouse_data.csv"
DASHBOARD_URL = "http://127.0.0"

bot = telebot.TeleBot("9157776843:AAFe4J0RCguua3SSjlkpNA4sWwdqhqsiyX8")
user_state = {}

# Инициализация CSV-файла со структурой из ЛР №5, если он отсутствует
def init_storage():
    if not os.path.exists(DATA_FILE):
        df = pd.DataFrame(columns=[
            "date", "operation", "category", "revenue", "expenses", "profit", "quantity"
        ])
        df.to_csv(DATA_FILE, index=False)

def main_keyboard():
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.row("📥 Приёмка", "📤 Отгрузка")
    kb.row("📋 Инвентаризация", "📊 Дашборд и аналитика")
    return kb

@bot.message_handler(commands=["start"])
def cmd_start(message):
    init_storage()
    bot.send_message(
        message.chat.id,
        "🏭 *WMS-Lite Bot — Управление складом*\n\n"
        "Выберите складскую операцию или откройте аналитику:",
        parse_mode="Markdown",
        reply_markup=main_keyboard()
    )

@bot.message_handler(func=lambda m: m.text in ["📥 Приёмка", "📤 Отгрузка", "📋 Инвентаризация"])
def select_operation(message):
    op_map = {
        "📥 Приёмка": "Приёмка",
        "📤 Отгрузка": "Отгрузка",
        "📋 Инвентаризация": "Инвентаризация"
    }
    user_state[message.chat.id] = {"operation": op_map[message.text]}

    kb = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    kb.row("Электроника", "Одежда", "Продукты")
    bot.send_message(message.chat.id, "Выберите категорию товара:", reply_markup=kb)

@bot.message_handler(func=lambda m: m.chat.id in user_state and "category" not in user_state[m.chat.id])
def select_category(message):
    user_state[message.chat.id]["category"] = message.text
    bot.send_message(
        message.chat.id,
        "Введите через пробел: *количество*, *выручку (₽)* и *расходы (₽)*\n"
        "Пример: `15 120000 50000`",
        parse_mode="Markdown",
        reply_markup=types.ReplyKeyboardRemove()
    )

@bot.message_handler(func=lambda m: m.chat.id in user_state and "category" in user_state[m.chat.id])
def save_record(message):
    try:
        qty_str, rev_str, exp_str = message.text.strip().split()
        quantity = int(qty_str)
        revenue = float(rev_str)
        expenses = float(exp_str)
        if quantity <= 0 or revenue < 0 or expenses < 0:
            raise ValueError
    except ValueError:
        bot.send_message(message.chat.id, "⚠️ Ошибка формата. Введите 3 числа через пробел, например: `10 50000 20000`", parse_mode="Markdown")
        return

    profit = revenue - expenses
    state = user_state.pop(message.chat.id)
    new_row = pd.DataFrame([{
        "date": datetime.now().strftime("%Y-%m-%d"),
        "operation": state["operation"],
        "category": state["category"],
        "revenue": revenue,
        "expenses": expenses,
        "profit": profit,
        "quantity": quantity
    }])

    df = pd.read_csv(DATA_FILE)
    df = pd.concat([df, new_row], ignore_index=True)
    df.to_csv(DATA_FILE, index=False)

    bot.send_message(
        message.chat.id,
        f"✅ *Операция записана в базу склада!*\n"
        f"• Тип: {state['operation']}\n"
        f"• Категория: {state['category']}\n"
        f"• Количество: {quantity} шт.\n"
        f"• Прибыль по операции: {profit:,.0f} ₽",
        parse_mode="Markdown",
        reply_markup=main_keyboard()
    )

@bot.message_handler(func=lambda m: m.text == "📊 Дашборд и аналитика")
def send_dashboard(message):
    init_storage()
    df = pd.read_csv(DATA_FILE)
    if df.empty:
        bot.send_message(message.chat.id, "База операций пока пуста.")
        return

    total_rev = df["revenue"].sum()
    total_exp = df["expenses"].sum()
    total_prof = df["profit"].sum()

    # Генерация мини-дашборда (прибыль по категориям)
    grouped = df.groupby("category")["profit"].sum()
    plt.figure(figsize=(6, 4))
    grouped.plot(kind="bar", color=["#4A6FE3", "#E35D4A", "#2AB57D"])
    plt.title("Прибыль склада по категориям (₽)")
    plt.ylabel("Прибыль, ₽")
    plt.xticks(rotation=0)
    plt.tight_layout()
    chart_path = "dashboard_summary.png"
    plt.savefig(chart_path)
    plt.close()

    caption = (
        f"📊 *Сводный дашборд склада*\n\n"
        f"💰 Выручка: *{total_rev:,.0f} ₽*\n"
        f"📉 Расходы: *{total_exp:,.0f} ₽*\n"
        f"📈 Чистая прибыль: *{total_prof:,.0f} ₽*\n"
        f"📦 Всего записей: *{len(df)}*\n\n"
        f"🌐 Интерактивный веб-дашборд Dash:\n`{DASHBOARD_URL}`"
    )
    with open(chart_path, "rb") as photo:
        bot.send_photo(message.chat.id, photo, caption=caption, parse_mode="Markdown")

if __name__ == "__main__":
    init_storage()
    print("Бот запущен...")
    bot.infinity_polling()