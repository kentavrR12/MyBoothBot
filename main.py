"""
Exhibition Booth Configurator Bot v15 (PRO)
- Integrated SQLite Database for order history
- Automatic PDF Report Generation
- Telegram Mini App support
- Multilingual support (EN, RUS, LV)
- ALL original handlers and back buttons preserved
"""

import os
import logging
import json
import datetime
from contextlib import suppress
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, F, Router
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, FSInputFile, WebAppInfo
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters import Command
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.exceptions import TelegramBadRequest
import urllib.parse

# Import custom modules
from database import init_db, add_user, save_order, get_user_orders
from pdf_generator import generate_order_pdf

# Load environment variables
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
PAYMENT_TOKEN = os.getenv("PAYMENT_TOKEN") # Нужно получить у @BotFather
CONFIGURATOR_URL = os.getenv("CONFIGURATOR_URL", "https://kentavrr12.github.io/my-booth-3d/")

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN not found in environment variables. Check your .env file")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize bot and dispatcher
bot = Bot(token=BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)
router = Router()

# ============================================================================
# STATES
# ============================================================================

class ConfigurationStates(StatesGroup):
    selecting_language = State()
    choosing_length = State()
    choosing_width = State()
    choosing_construction_type = State()
    choosing_materials = State()
    choosing_equipment = State()
    confirmation = State()
    final_report = State()

# ============================================================================
# CONFIGURATION DATA
# ============================================================================

LENGTHS = [2.0, 3.0, 4.0, 5.0, 6.0]
WIDTHS = [2.0, 3.0, 4.0, 5.0]

CONSTRUCTION_TYPES = {
    "standard": {"name_en": "Standard", "name_ru": "Стандартный", "name_lv": "Standarts", "price": 500.0},
    "exclusive": {"name_en": "Exclusive", "name_ru": "Эксклюзивный", "name_lv": "Ekskluzīvs", "price": 800.0}
}

MATERIALS = {
    "plastic": {"name_en": "Plastic", "name_ru": "Пластик", "name_lv": "Plastmasa", "price": 50.0},
    "wood": {"name_en": "Wood", "name_ru": "Дерево", "name_lv": "Koks", "price": 150.0},
    "metal": {"name_en": "Metal", "name_ru": "Металл", "name_lv": "Metāls", "price": 200.0}
}

EQUIPMENT = {
    "lighting": {"name_en": "Lighting", "name_ru": "Освещение", "name_lv": "Apgaismojums", "price": 300.0},
    "furniture": {"name_en": "Furniture", "name_ru": "Мебель", "name_lv": "Mēbeles", "price": 400.0},
    "monitor": {"name_en": "Monitor", "name_ru": "Монитор", "name_lv": "Monitors", "price": 800.0}
}

# ============================================================================
# TRANSLATIONS
# ============================================================================

TEXTS = {
    "EN": {
        "welcome": "🎉 **Welcome to Exhibition Booth Configurator!**\n\nLet's create your perfect booth. Click 'Start Configuration' to begin.",
        "3d_configurator": "🎨 Open 3D Configurator",
        "quick_config": "⚙️ Start Configuration",
        "3d_description": "Click the button below to open the 3D visualizer with your current settings.",
        "step_length": "📏 **Select booth length (in meters):**",
        "step_width": "📐 **Select booth width (in meters):**",
        "step_construction": "🏗️ **Select construction type:**",
        "step_materials": "🎨 **Select materials (you can choose multiple):**",
        "step_equipment": "⚙️ **Select additional equipment (you can choose multiple):**",
        "selected_length": "✅ Length: {length}m",
        "selected_width": "✅ Width: {width}m",
        "selected_area": "📊 Area: {area}m²",
        "selected_construction": "🏗️ Type: {construction}",
        "selected_materials": "🎨 Materials: {materials}",
        "selected_equipment": "⚙️ Equipment: {equipment}",
        "none_selected": "None",
        "calculate": "💰 Calculate Total",
        "confirm": "✅ Confirm Order",
        "cancel": "❌ Cancel",
        "back": "⬅️ Back",
        "order_confirmed": "🎉 **Order Confirmed!**\n\nYour PDF summary is being generated...",
        "main_menu": "🏠 Main Menu",
        "canceled": "❌ Configuration canceled. Select language to start again.",
        "cost_summary": "💰 **COST SUMMARY**\n\n",
        "base_price": "Base booth: ",
        "materials_cost": "Materials: ",
        "equipment_cost": "Equipment: ",
        "total_price": "\n**TOTAL: {total}€**",
        "error_calc": "❌ Error calculating cost. Please try again."
    },
    "RUS": {
        "welcome": "🎉 **Добро пожаловать в Конфигуратор Выставочных Стендов!**\n\nДавайте создадим ваш идеальный стенд. Нажмите 'Начать конфигурацию'.",
        "3d_configurator": "🎨 Открыть 3D конфигуратор",
        "quick_config": "⚙️ Начать конфигурацию",
        "3d_description": "Нажмите кнопку ниже, чтобы открыть 3D визуализатор с вашими настройками.",
        "step_length": "📏 **Выберите длину стенда (в метрах):**",
        "step_width": "📐 **Выберите ширину стенда (в метрах):**",
        "step_construction": "🏗️ **Выберите тип конструкции:**",
        "step_materials": "🎨 **Выберите материалы (можно выбрать несколько):**",
        "step_equipment": "⚙️ **Выберите дополнительное оборудование (можно выбрать несколько):**",
        "selected_length": "✅ Длина: {length}м",
        "selected_width": "✅ Ширина: {width}м",
        "selected_area": "📊 Площадь: {area}м²",
        "selected_construction": "🏗️ Тип: {construction}",
        "selected_materials": "🎨 Материалы: {materials}",
        "selected_equipment": "⚙️ Оборудование: {equipment}",
        "none_selected": "Не выбрано",
        "calculate": "💰 Рассчитать",
        "confirm": "✅ Подтвердить заказ",
        "cancel": "❌ Отмена",
        "back": "⬅️ Назад",
        "order_confirmed": "🎉 **Заказ подтвержден!**\n\nВаша смета в формате PDF формируется...",
        "main_menu": "🏠 Главное меню",
        "canceled": "❌ Конфигурация отменена. Выберите язык, чтобы начать заново.",
        "cost_summary": "💰 **СМЕТА СТОИМОСТИ**\n\n",
        "base_price": "Базовый стенд: ",
        "materials_cost": "Материалы: ",
        "equipment_cost": "Оборудование: ",
        "total_price": "\n**ИТОГО: {total}€**",
        "error_calc": "❌ Ошибка при расчете стоимости. Попробуйте еще раз."
    },
    "LV": {
        "welcome": "🎉 **Sveicināti Exhibition Booth Configurator!**\n\nVeidosim jūsu ideālo stendu. Noklikšķiniet uz 'Sākt konfigurāciju'.",
        "3d_configurator": "🎨 Atvērt 3D konfiguratoru",
        "quick_config": "⚙️ Sākt konfigurāciju",
        "3d_description": "Noklikšķiniet uz pogas zemāk, lai atvērtu 3D vizualizatoru ar jūsu iestatījumiem.",
        "step_length": "📏 **Izvēlieties stenda garumu (metros):**",
        "step_width": "📐 **Izvēlieties stenda platumu (metros):**",
        "step_construction": "🏗️ **Izvēlieties konstrukcijas tipu:**",
        "step_materials": "🎨 **Izvēlieties materiālus (varat izvēlēties vairākus):**",
        "step_equipment": "⚙️ **Izvēlieties papildu aprīkojumu (varat izvēlēties vairākus):**",
        "selected_length": "✅ Garums: {length}m",
        "selected_width": "✅ Platums: {width}m",
        "selected_area": "📊 Platība: {area}m²",
        "selected_construction": "🏗️ Tips: {construction}",
        "selected_materials": "🎨 Materiāli: {materials}",
        "selected_equipment": "⚙️ Aprīkojums: {equipment}",
        "none_selected": "Nav izvēlēts",
        "calculate": "💰 Aprēķināt kopējo",
        "confirm": "✅ Apstiprināt pasūtījumu",
        "cancel": "❌ Atcelt",
        "back": "⬅️ Atpakaļ",
        "order_confirmed": "🎉 **Pasūtījums apstiprināts!**\n\nJūsu PDF tāme tiek sagatavota...",
        "main_menu": "🏠 Galvenā izvēlne",
        "canceled": "❌ Konfigurācija atcelta. Izvēlieties valodu, lai sāktu no jauna.",
        "cost_summary": "💰 **IZMAKSU KOPSAVILKUMS**\n\n",
        "base_price": "Pamatne stendam: ",
        "materials_cost": "Materiāli: ",
        "equipment_cost": "Aprīkojums: ",
        "total_price": "\n**KOPĀ: {total}€**",
        "error_calc": "❌ Kļūda aprēķinot izmaksas. Lūdzu, mēģiniet vēlreiz."
    }
}

def get_text(language, key, **kwargs):
    """Get translated text."""
    text = TEXTS.get(language, TEXTS["EN"]).get(key, "")
    return text.format(**kwargs) if kwargs else text

# ============================================================================
# KEYBOARD BUILDERS
# ============================================================================

def get_language_keyboard():
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🇬🇧 English", callback_data="lang_EN")],
        [InlineKeyboardButton(text="🇷🇺 Русский", callback_data="lang_RUS")],
        [InlineKeyboardButton(text="🇱🇻 Latviešu", callback_data="lang_LV")]
    ])
    return kb

def get_start_keyboard(language, url=None):
    if not url:
        url = CONFIGURATOR_URL
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=get_text(language, "3d_configurator"), web_app=WebAppInfo(url=url))],
        [InlineKeyboardButton(text=get_text(language, "quick_config"), callback_data="start_config")]
    ])
    return kb

def get_length_keyboard(language):
    buttons = [[InlineKeyboardButton(text=f"{l}м", callback_data=f"length_{l}")] for l in LENGTHS]
    kb = InlineKeyboardMarkup(inline_keyboard=buttons)
    return kb

def get_width_keyboard(language):
    buttons = [[InlineKeyboardButton(text=f"{w}м", callback_data=f"width_{w}")] for w in WIDTHS]
    buttons.append([InlineKeyboardButton(text=get_text(language, "back"), callback_data="back_to_length")])
    kb = InlineKeyboardMarkup(inline_keyboard=buttons)
    return kb

def get_construction_keyboard(language):
    buttons = []
    for key, val in CONSTRUCTION_TYPES.items():
        name = val.get(f"name_{language.lower()}", val["name_en"])
        price = val["price"]
        buttons.append([InlineKeyboardButton(text=f"{name} +{price:.0f}€", callback_data=f"construction_{key}")])
    buttons.append([InlineKeyboardButton(text=get_text(language, "back"), callback_data="back_to_width")])
    kb = InlineKeyboardMarkup(inline_keyboard=buttons)
    return kb

def get_materials_keyboard(language, selected_materials):
    buttons = []
    for key, val in MATERIALS.items():
        name = val.get(f"name_{language.lower()}", val["name_en"])
        price = val["price"]
        check = "✅" if key in selected_materials else "☐"
        buttons.append([InlineKeyboardButton(text=f"{check} {name} +{price:.0f}€/м²", callback_data=f"material_{key}")])
    buttons.append([InlineKeyboardButton(text=get_text(language, "calculate"), callback_data="materials_done")])
    buttons.append([InlineKeyboardButton(text=get_text(language, "back"), callback_data="back_to_construction")])
    kb = InlineKeyboardMarkup(inline_keyboard=buttons)
    return kb

def get_equipment_keyboard(language, selected_equipment):
    buttons = []
    for key, val in EQUIPMENT.items():
        name = val.get(f"name_{language.lower()}", val["name_en"])
        price = val["price"]
        check = "✅" if key in selected_equipment else "☐"
        buttons.append([InlineKeyboardButton(text=f"{check} {name} +{price:.0f}€", callback_data=f"equipment_{key}")])
    buttons.append([InlineKeyboardButton(text=get_text(language, "calculate"), callback_data="equipment_done")])
    buttons.append([InlineKeyboardButton(text=get_text(language, "back"), callback_data="back_to_materials")])
    kb = InlineKeyboardMarkup(inline_keyboard=buttons)
    return kb

def get_confirmation_keyboard(language):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=get_text(language, "confirm"), callback_data="confirm_order")],
        [InlineKeyboardButton(text=get_text(language, "cancel"), callback_data="cancel")]
    ])
    return kb

def get_final_keyboard(language):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=get_text(language, "main_menu"), callback_data="main_menu")]
    ])
    return kb

def get_configurator_url(length, width, construction, materials, equipment):
    params = {
        'length': str(length),
        'width': str(width),
        'construction': construction,
        'materials': ','.join(materials) if materials else '',
        'equipment': ','.join(equipment) if equipment else ''
    }
    query_string = urllib.parse.urlencode(params)
    return CONFIGURATOR_URL + f"?{query_string}"

# ============================================================================
# COST CALCULATION
# ============================================================================

def calculate_cost(length, width, construction_type, materials, equipment):
    try:
        length = float(length) if length else 2.0
        width = float(width) if width else 2.0
        base_price = CONSTRUCTION_TYPES.get(construction_type, CONSTRUCTION_TYPES["standard"])["price"]
        area = length * width
        base_total = base_price * area
        materials_total = sum([MATERIALS[m]["price"] * area for m in materials if m in MATERIALS])
        equipment_total = sum([EQUIPMENT[e]["price"] for e in equipment if e in EQUIPMENT])
        total = base_total + materials_total + equipment_total
        return {"base": base_total, "materials": materials_total, "equipment": equipment_total, "total": total}
    except Exception as e:
        logger.error(f"Error in calculation: {e}")
        return {"base": 0, "materials": 0, "equipment": 0, "total": 0}

def format_cost_summary(language, length, width, construction_type, materials, equipment):
    costs = calculate_cost(length, width, construction_type, materials, equipment)
    summary = get_text(language, "cost_summary")
    summary += f"{get_text(language, 'base_price')}{costs['base']:.2f}€\n"
    summary += f"{get_text(language, 'materials_cost')}{costs['materials']:.2f}€\n"
    summary += f"{get_text(language, 'equipment_cost')}{costs['equipment']:.2f}€"
    summary += get_text(language, "total_price", total=f"{costs['total']:.2f}")
    return summary

# ============================================================================
# HANDLERS
# ============================================================================

# ADMIN_ID = 12345678  # Раскомментируй и впиши свой ID для уведомлений

@router.message(F.photo)
async def handle_logo(message: Message, state: FSMContext):
    """Handle logo upload for the booth."""
    data = await state.get_data()
    language = data.get("language", "EN")
    
    # Create directory if not exists
    os.makedirs("logos", exist_ok=True)
    
    file_id = message.photo[-1].file_id
    file = await bot.get_file(file_id)
    file_path = f"logos/logo_{message.from_user.id}.png"
    await bot.download_file(file.file_path, file_path)
    
    await state.update_data(logo_path=file_path)
    
    msg = {
        "EN": "✅ **Logo uploaded!** It will be applied to your 3D booth walls.",
        "RUS": "✅ **Логотип загружен!** Он будет размещен на стенах вашего 3D стенда.",
        "LV": "✅ **Logotips augšupielādēts!** Tas tiks izvietots uz jūsu 3D stenda sienām."
    }
    await message.answer(msg.get(language, msg["EN"]))

@router.message(Command("start"))
async def cmd_start(message: Message, state: FSMContext) -> None:
    await state.clear()
    await state.set_state(ConfigurationStates.selecting_language)
    await message.answer(
        "Выберите язык / Select language / Izvēlieties valodu:",
        reply_markup=get_language_keyboard()
    )

@router.callback_query(F.data.startswith("lang_"))
async def select_language(callback: CallbackQuery, state: FSMContext) -> None:
    language = callback.data.split("_")[1]
    await state.update_data(language=language)
    
    # Save user to DB
    await add_user(
        callback.from_user.id, 
        callback.from_user.username, 
        callback.from_user.full_name, 
        language
    )
    
    url = get_configurator_url(3.0, 3.0, "standard", [], [])
    await callback.message.edit_text(
        get_text(language, "welcome"),
        reply_markup=get_start_keyboard(language, url)
    )
    await callback.answer()

@router.callback_query(F.data == "start_config")
async def start_configuration(callback: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    language = data.get("language", "EN")
    await state.set_state(ConfigurationStates.choosing_length)
    await callback.message.edit_text(
        get_text(language, "step_length"),
        reply_markup=get_length_keyboard(language)
    )
    await callback.answer()

@router.callback_query(F.data.startswith("length_"))
async def choose_length(callback: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    language = data.get("language", "EN")
    length = float(callback.data.split("_")[1])
    await state.update_data(length=length)
    await state.set_state(ConfigurationStates.choosing_width)
    summary = get_text(language, "selected_length", length=length) + "\n\n" + get_text(language, "step_width")
    await callback.message.edit_text(summary, reply_markup=get_width_keyboard(language))
    await callback.answer()

@router.callback_query(F.data.startswith("width_"))
async def choose_width(callback: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    language = data.get("language", "EN")
    width = float(callback.data.split("_")[1])
    await state.update_data(width=width)
    await state.set_state(ConfigurationStates.choosing_construction_type)
    length = data.get("length", 2.0)
    area = length * width
    summary = get_text(language, "selected_length", length=length) + "\n" + get_text(language, "selected_width", width=width) + "\n" + get_text(language, "selected_area", area=area) + "\n\n" + get_text(language, "step_construction")
    await callback.message.edit_text(summary, reply_markup=get_construction_keyboard(language))
    await callback.answer()

@router.callback_query(F.data.startswith("construction_"))
async def choose_construction(callback: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    language = data.get("language", "EN")
    construction_type = callback.data.split("_")[1]
    construction_name = CONSTRUCTION_TYPES[construction_type].get(f"name_{language.lower()}", CONSTRUCTION_TYPES[construction_type]["name_en"])
    await state.update_data(construction_type=construction_type)
    await state.set_state(ConfigurationStates.choosing_materials)
    length = data.get("length", 2.0)
    width = data.get("width", 2.0)
    area = length * width
    summary = get_text(language, "selected_length", length=length) + "\n" + get_text(language, "selected_width", width=width) + "\n" + get_text(language, "selected_area", area=area) + "\n" + get_text(language, "selected_construction", construction=construction_name) + "\n\n" + get_text(language, "step_materials")
    await callback.message.edit_text(summary, reply_markup=get_materials_keyboard(language, []))
    await callback.answer()

@router.callback_query(F.data.startswith("material_"))
async def toggle_material(callback: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    language = data.get("language", "EN")
    material_key = callback.data.split("_")[1]
    materials = data.get("materials", [])
    if material_key in materials:
        materials.remove(material_key)
    else:
        materials.append(material_key)
    await state.update_data(materials=materials)
    with suppress(TelegramBadRequest):
        await callback.message.edit_reply_markup(reply_markup=get_materials_keyboard(language, materials))
    await callback.answer()

@router.callback_query(F.data == "materials_done")
async def materials_done(callback: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    language = data.get("language", "EN")
    await state.set_state(ConfigurationStates.choosing_equipment)
    length = data.get("length", 2.0)
    width = data.get("width", 2.0)
    area = length * width
    construction_type = data.get("construction_type", "standard")
    construction_name = CONSTRUCTION_TYPES[construction_type].get(f"name_{language.lower()}", CONSTRUCTION_TYPES[construction_type]["name_en"])
    materials = data.get("materials", [])
    materials_text = ", ".join([MATERIALS[m].get(f"name_{language.lower()}", MATERIALS[m]["name_en"]) for m in materials if m in MATERIALS]) or get_text(language, "none_selected")
    summary = get_text(language, "selected_length", length=length) + "\n" + get_text(language, "selected_width", width=width) + "\n" + get_text(language, "selected_area", area=area) + "\n" + get_text(language, "selected_construction", construction=construction_name) + "\n" + get_text(language, "selected_materials", materials=materials_text) + "\n\n" + get_text(language, "step_equipment")
    await callback.message.edit_text(summary, reply_markup=get_equipment_keyboard(language, []))
    await callback.answer()

@router.callback_query(F.data.startswith("equipment_"))
async def toggle_equipment(callback: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    language = data.get("language", "EN")
    equipment_key = callback.data.split("_")[1]
    equipment = data.get("equipment", [])
    if equipment_key in equipment:
        equipment.remove(equipment_key)
    else:
        equipment.append(equipment_key)
    await state.update_data(equipment=equipment)
    with suppress(TelegramBadRequest):
        await callback.message.edit_reply_markup(reply_markup=get_equipment_keyboard(language, equipment))
    await callback.answer()

@router.callback_query(F.data == "equipment_done")
async def equipment_done(callback: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    language = data.get("language", "EN")
    summary = format_cost_summary(language, data.get("length", 2.0), data.get("width", 2.0), data.get("construction_type", "standard"), data.get("materials", []), data.get("equipment", []))
    await state.set_state(ConfigurationStates.confirmation)
    await callback.message.edit_text(summary, reply_markup=get_confirmation_keyboard(language))
    await callback.answer()

@router.callback_query(F.data == "confirm_order")
async def confirm_order(callback: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    language = data.get("language", "EN")
    
    # Calculate final costs
    costs = calculate_cost(
        data.get("length", 2.0), 
        data.get("width", 2.0), 
        data.get("construction_type", "standard"), 
        data.get("materials", []), 
        data.get("equipment", [])
    )
    
    # Save to Database
    await save_order(
        callback.from_user.id,
        data.get("length", 2.0),
        data.get("width", 2.0),
        data.get("construction_type", "standard"),
        data.get("materials", []),
        data.get("equipment", []),
        costs["total"]
    )
    
    # Prepare PDF Data
    order_data = {
        "order_id": datetime.datetime.now().strftime("%Y%m%d%H%M"),
        "date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
        "length": data.get("length", 2.0),
        "width": data.get("width", 2.0),
        "construction_name": CONSTRUCTION_TYPES[data.get("construction_type", "standard")]["name_en"],
        "materials_names": [MATERIALS[m]["name_en"] for m in data.get("materials", [])],
        "equipment_names": [EQUIPMENT[e]["name_en"] for e in data.get("equipment", [])],
        "total_price": costs["total"]
    }
    
    pdf_filename = f"order_{callback.from_user.id}_{order_data['order_id']}.pdf"
    generate_order_pdf(order_data, pdf_filename)
    
    await state.set_state(ConfigurationStates.final_report)
    await callback.message.edit_text(get_text(language, 'order_confirmed'), reply_markup=get_final_keyboard(language))
    
    # Send PDF
    pdf_file = FSInputFile(pdf_filename)
    await callback.message.answer_document(pdf_file, caption="📄 Your Booth Order Summary (PDF)")
    
    # Cleanup PDF file after sending
    with suppress(Exception):
        os.remove(pdf_filename)
    
    # Payment Option (Mockup/Test)
    if PAYMENT_TOKEN:
        await callback.message.answer_invoice(
            title="Booth Reservation",
            description=f"Reservation for {data.get('length')}x{data.get('width')} booth",
            payload="booth_order_payload",
            provider_token=PAYMENT_TOKEN,
            currency="EUR",
            prices=[{"label": "Deposit", "amount": int(costs['total'] * 100)}], # Amount in cents
            start_parameter="booth_order"
        )
        
    await callback.answer()

@router.pre_checkout_query()
async def pre_checkout_query(query):
    await bot.answer_pre_checkout_query(query.id, ok=True)

@router.message(F.successful_payment)
async def successful_payment(message: Message):
    await message.answer("✅ Payment successful! Our manager will contact you soon.")

# BACK BUTTONS & MENU
@router.callback_query(F.data == "back_to_length")
async def back_to_length(callback: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    language = data.get("language", "EN")
    await state.set_state(ConfigurationStates.choosing_length)
    await callback.message.edit_text(get_text(language, "step_length"), reply_markup=get_length_keyboard(language))
    await callback.answer()

@router.callback_query(F.data == "back_to_width")
async def back_to_width(callback: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    language = data.get("language", "EN")
    await state.set_state(ConfigurationStates.choosing_width)
    length = data.get("length", 2.0)
    summary = get_text(language, "selected_length", length=length) + "\n\n" + get_text(language, "step_width")
    await callback.message.edit_text(summary, reply_markup=get_width_keyboard(language))
    await callback.answer()

@router.callback_query(F.data == "back_to_construction")
async def back_to_construction(callback: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    language = data.get("language", "EN")
    await state.set_state(ConfigurationStates.choosing_construction_type)
    length = data.get("length", 2.0)
    width = data.get("width", 2.0)
    area = length * width
    summary = get_text(language, "selected_length", length=length) + "\n" + get_text(language, "selected_width", width=width) + "\n" + get_text(language, "selected_area", area=area) + "\n\n" + get_text(language, "step_construction")
    await callback.message.edit_text(summary, reply_markup=get_construction_keyboard(language))
    await callback.answer()

@router.callback_query(F.data == "back_to_materials")
async def back_to_materials(callback: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    language = data.get("language", "EN")
    await state.set_state(ConfigurationStates.choosing_materials)
    length = data.get("length", 2.0)
    width = data.get("width", 2.0)
    area = length * width
    construction_type = data.get("construction_type", "standard")
    construction_name = CONSTRUCTION_TYPES[construction_type].get(f"name_{language.lower()}", CONSTRUCTION_TYPES[construction_type]["name_en"])
    materials = data.get("materials", [])
    summary = get_text(language, "selected_length", length=length) + "\n" + get_text(language, "selected_width", width=width) + "\n" + get_text(language, "selected_area", area=area) + "\n" + get_text(language, "selected_construction", construction=construction_name) + "\n\n" + get_text(language, "step_materials")
    await callback.message.edit_text(summary, reply_markup=get_materials_keyboard(language, materials))
    await callback.answer()

@router.callback_query(F.data == "back_to_equipment")
async def back_to_equipment(callback: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    language = data.get("language", "EN")
    await state.set_state(ConfigurationStates.choosing_equipment)
    length = data.get("length", 2.0)
    width = data.get("width", 2.0)
    area = length * width
    construction_type = data.get("construction_type", "standard")
    construction_name = CONSTRUCTION_TYPES[construction_type].get(f"name_{language.lower()}", CONSTRUCTION_TYPES[construction_type]["name_en"])
    materials = data.get("materials", [])
    materials_text = ", ".join([MATERIALS[m].get(f"name_{language.lower()}", MATERIALS[m]["name_en"]) for m in materials if m in MATERIALS]) or get_text(language, "none_selected")
    equipment = data.get("equipment", [])
    summary = get_text(language, "selected_length", length=length) + "\n" + get_text(language, "selected_width", width=width) + "\n" + get_text(language, "selected_area", area=area) + "\n" + get_text(language, "selected_construction", construction=construction_name) + "\n" + get_text(language, "selected_materials", materials=materials_text) + "\n\n" + get_text(language, "step_equipment")
    await callback.message.edit_text(summary, reply_markup=get_equipment_keyboard(language, equipment))
    await callback.answer()

@router.callback_query(F.data == "cancel")
async def cancel(callback: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    language = data.get("language", "EN")
    await state.clear()
    await state.update_data(language=language)
    await callback.message.edit_text(get_text(language, "canceled"), reply_markup=get_start_keyboard(language))
    await callback.answer()

@router.callback_query(F.data == "main_menu")
async def main_menu(callback: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    language = data.get("language", "EN")
    await state.clear()
    await state.update_data(language=language)
    await callback.message.edit_text(get_text(language, "welcome"), reply_markup=get_start_keyboard(language))
    await callback.answer()

async def main() -> None:
    await init_db()
    dp.include_router(router)
    try:
        logger.info("🤖 BOT IS RUNNING AND READY TO WORK...")
        await dp.start_polling(bot)
    finally:
        await bot.session.close()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
