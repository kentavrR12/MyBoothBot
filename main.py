"""
Exhibition Booth Configurator Bot v13 (FIXED)
- Telegram Bot with 3D Web Configurator integration
- FIXED: Russian language now in Cyrillic (not Latin)
- FIXED: Working configurator links
- Multilingual support (EN, RUS, LV)
- Cost calculation
- Link to 3D configurator
"""

import os
import logging
from contextlib import suppress
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, F, Router
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters import Command
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.exceptions import TelegramBadRequest
import urllib.parse

# Load environment variables
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
# Используем локальный конфигуратор по умолчанию
CONFIGURATOR_URL = os.getenv("CONFIGURATOR_URL", "http://localhost:8000/")

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN not found in environment variables. Check your .env file")

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
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
    "exclusive": {"name_en": "Exclusive", "name_ru": "Эксклюзивный", "name_lv": "Eksklusivs", "price": 800.0}
}

MATERIALS = {
    "plastic": {"name_en": "Plastic", "name_ru": "Пластик", "name_lv": "Plastmasa", "price": 50.0},
    "wood": {"name_en": "Wood", "name_ru": "Дерево", "name_lv": "Koks", "price": 150.0},
    "metal": {"name_en": "Metal", "name_ru": "Металл", "name_lv": "Metals", "price": 200.0}
}

EQUIPMENT = {
    "lighting": {"name_en": "Lighting", "name_ru": "Освещение", "name_lv": "Apgaismojums", "price": 300.0},
    "furniture": {"name_en": "Furniture", "name_ru": "Мебель", "name_lv": "Mebeles", "price": 400.0},
    "monitor": {"name_en": "Monitor", "name_ru": "Монитор", "name_lv": "Monitors", "price": 800.0}
}

# ============================================================================
# TRANSLATIONS (FIXED: Russian in Cyrillic)
# ============================================================================

TEXTS = {
    "EN": {
        "welcome": "Welcome to Exhibition Booth Configurator!\n\nLet's create your perfect booth. Click 'Start Configuration' to begin.",
        "step_length": "Select booth length (in meters):",
        "step_width": "Select booth width (in meters):",
        "step_construction": "Select construction type:",
        "step_materials": "Select materials (you can choose multiple):",
        "step_equipment": "Select additional equipment (you can choose multiple):",
        "selected_length": "Length: {length}m",
        "selected_width": "Width: {width}m",
        "selected_area": "Area: {area}m²",
        "selected_construction": "Type: {construction}",
        "selected_materials": "Materials: {materials}",
        "selected_equipment": "Equipment: {equipment}",
        "none_selected": "None",
        "calculate": "Calculate Total",
        "confirm": "Confirm Order",
        "cancel": "Cancel",
        "back": "Back",
        "order_confirmed": "Order Confirmed!\n\nThank you for using our service!",
        "main_menu": "Main Menu",
        "canceled": "Configuration canceled. Select language to start again.",
        "cost_summary": "COST SUMMARY\n\n",
        "base_price": "Base booth: ",
        "materials_cost": "Materials: ",
        "equipment_cost": "Equipment: ",
        "total_price": "\nTOTAL: {total} EUR",
        "error_calc": "Error calculating cost. Please try again.",
        "3d_configurator": "Design in 3D",
        "3d_description": "Open our interactive 3D configurator to visualize your booth design in real-time. You can rotate, zoom, and customize colors, materials, and equipment.",
        "quick_config": "Quick Config",
        "quick_config_desc": "Or configure quickly using buttons below."
    },
    "RUS": {
        "welcome": "Добро пожаловать в Конфигуратор Выставочных Стендов!\n\nДавайте создадим ваш идеальный стенд. Нажмите 'Начать конфигурацию'.",
        "step_length": "Выберите длину стенда (в метрах):",
        "step_width": "Выберите ширину стенда (в метрах):",
        "step_construction": "Выберите тип конструкции:",
        "step_materials": "Выберите материалы (можно выбрать несколько):",
        "step_equipment": "Выберите дополнительное оборудование (можно выбрать несколько):",
        "selected_length": "Длина: {length}м",
        "selected_width": "Ширина: {width}м",
        "selected_area": "Площадь: {area}м²",
        "selected_construction": "Тип: {construction}",
        "selected_materials": "Материалы: {materials}",
        "selected_equipment": "Оборудование: {equipment}",
        "none_selected": "Не выбрано",
        "calculate": "Рассчитать",
        "confirm": "Подтвердить заказ",
        "cancel": "Отмена",
        "back": "Назад",
        "order_confirmed": "Заказ подтвержден!\n\nСпасибо за использование нашего сервиса!",
        "main_menu": "Главное меню",
        "canceled": "Конфигурация отменена. Выберите язык, чтобы начать заново.",
        "cost_summary": "СМЕТА СТОИМОСТИ\n\n",
        "base_price": "Базовый стенд: ",
        "materials_cost": "Материалы: ",
        "equipment_cost": "Оборудование: ",
        "total_price": "\nИТОГО: {total} EUR",
        "error_calc": "Ошибка при расчете стоимости. Попробуйте еще раз.",
        "3d_configurator": "Дизайн в 3D",
        "3d_description": "Откройте наш интерактивный 3D конфигуратор для визуализации дизайна стенда в реальном времени. Вы можете вращать, масштабировать и кастомизировать цвета, материалы и оборудование.",
        "quick_config": "Быстрая конфигурация",
        "quick_config_desc": "Или настройте быстро, используя кнопки ниже."
    },
    "LV": {
        "welcome": "Sveiki Exhibition Booth Configurator!\n\nVeidosim jusu idealo stendu. Noklikskinjiet uz 'Sakt konfiguraciju'.",
        "step_length": "Izveljieties stendu garumu (metros):",
        "step_width": "Izveljieties stendu platumu (metros):",
        "step_construction": "Izveljieties konstrukcijas tipu:",
        "step_materials": "Izveljieties materialus (varat izveljieties vairakus):",
        "step_equipment": "Izveljieties papildu aprikojumu (varat izveljieties vairakus):",
        "selected_length": "Garums: {length}m",
        "selected_width": "Platums: {width}m",
        "selected_area": "Platiba: {area}m²",
        "selected_construction": "Tips: {construction}",
        "selected_materials": "Materiali: {materials}",
        "selected_equipment": "Aprikojums: {equipment}",
        "none_selected": "Nav izveljets",
        "calculate": "Aprekjinat kopejo",
        "confirm": "Apstiprinat pasutijumu",
        "cancel": "Atcelt",
        "back": "Atpakaj",
        "order_confirmed": "Pasutijums apstiprinats!\n\nPaldies par musu pakalpojuma izmantosanu!",
        "main_menu": "Galvena izvejne",
        "canceled": "Konfiguracija atcelta. Izveljieties valodu, lai saktu no jauna.",
        "cost_summary": "IZMAKSU KOPSAVILKUMS\n\n",
        "base_price": "Pamatne stendu: ",
        "materials_cost": "Materiali: ",
        "equipment_cost": "Aprikojums: ",
        "total_price": "\nKOPA: {total} EUR",
        "error_calc": "Kluda aprekjinat izmaksas. Ludzu, megjinat vejirez.",
        "3d_configurator": "Dizains 3D",
        "3d_description": "Atveriet musu interaktivo 3D konfiguratoru, lai vizualizetu stendu dizainu reala laika. Varat griezt, maskalit un personalizet krasas, materialus un aprikojumu.",
        "quick_config": "Atrais Konfiguracija",
        "quick_config_desc": "Vai konfigurējiet ātri, izmantojot pogas zemāk."
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
    """Language selection keyboard."""
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🇬🇧 English", callback_data="lang_EN")],
        [InlineKeyboardButton(text="🇷🇺 Русский", callback_data="lang_RUS")],
        [InlineKeyboardButton(text="🇱🇻 Latviešu", callback_data="lang_LV")]
    ])
    return kb

def get_start_keyboard(language):
    """Start menu keyboard."""
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=get_text(language, "3d_configurator"), callback_data="open_3d_configurator")],
        [InlineKeyboardButton(text=get_text(language, "quick_config"), callback_data="start_config")]
    ])
    return kb

def get_length_keyboard(language):
    """Length selection keyboard."""
    buttons = [[InlineKeyboardButton(text=f"{l}м", callback_data=f"length_{l}")] for l in LENGTHS]
    kb = InlineKeyboardMarkup(inline_keyboard=buttons)
    return kb

def get_width_keyboard(language):
    """Width selection keyboard."""
    buttons = [[InlineKeyboardButton(text=f"{w}м", callback_data=f"width_{w}")] for w in WIDTHS]
    buttons.append([InlineKeyboardButton(text=get_text(language, "back"), callback_data="back_to_length")])
    kb = InlineKeyboardMarkup(inline_keyboard=buttons)
    return kb

def get_construction_keyboard(language):
    """Construction type selection keyboard."""
    buttons = []
    for key, val in CONSTRUCTION_TYPES.items():
        name = val.get(f"name_{language.lower()}", val["name_en"])
        price = val["price"]
        buttons.append([InlineKeyboardButton(text=f"{name} +{price:.0f}€", callback_data=f"construction_{key}")])
    buttons.append([InlineKeyboardButton(text=get_text(language, "back"), callback_data="back_to_width")])
    kb = InlineKeyboardMarkup(inline_keyboard=buttons)
    return kb

def get_materials_keyboard(language, selected_materials):
    """Materials selection keyboard."""
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
    """Equipment selection keyboard."""
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
    """Confirmation keyboard."""
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=get_text(language, "confirm"), callback_data="confirm_order")],
        [InlineKeyboardButton(text=get_text(language, "cancel"), callback_data="cancel")]
    ])
    return kb

def get_final_keyboard(language):
    """Final menu keyboard."""
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=get_text(language, "main_menu"), callback_data="main_menu")]
    ])
    return kb

def get_3d_configurator_keyboard(language, length, width, construction, materials, equipment):
    """Generate 3D configurator link."""
    # URL-encode параметры
    params = {
        'length': str(length),
        'width': str(width),
        'construction': construction,
        'materials': ','.join(materials) if materials else '',
        'equipment': ','.join(equipment) if equipment else ''
    }
    
    # Формируем query string
    query_string = urllib.parse.urlencode(params)
    url = CONFIGURATOR_URL + f"?{query_string}"
    
    logger.info(f"Generated configurator URL: {url}")
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🎨 Открыть 3D конфигуратор" if language == "RUS" else "Open 3D Configurator", url=url)],
        [InlineKeyboardButton(text=get_text(language, "quick_config"), callback_data="start_config")],
        [InlineKeyboardButton(text=get_text(language, "main_menu"), callback_data="main_menu")]
    ])
    return kb, url

# ============================================================================
# COST CALCULATION
# ============================================================================

def calculate_cost(length, width, construction_type, materials, equipment):
    """Calculate total cost."""
    try:
        length = float(length) if length else 2.0
        width = float(width) if width else 2.0
        
        base_price = CONSTRUCTION_TYPES.get(construction_type, CONSTRUCTION_TYPES["standard"])["price"]
        area = length * width
        base_total = base_price * area
        
        materials_total = 0.0
        for m in materials:
            if m in MATERIALS:
                materials_total += MATERIALS[m]["price"] * area
        
        equipment_total = 0.0
        for e in equipment:
            if e in EQUIPMENT:
                equipment_total += EQUIPMENT[e]["price"]
        
        total = base_total + materials_total + equipment_total
        
        logger.info(f"✅ COST CALCULATED: Base={base_total:.2f}€, Materials={materials_total:.2f}€, Equipment={equipment_total:.2f}€, TOTAL={total:.2f}€")
        
        return {
            "base": base_total,
            "materials": materials_total,
            "equipment": equipment_total,
            "total": total
        }
    except Exception as e:
        logger.error(f"❌ ERROR IN CALCULATION: {str(e)}")
        return {
            "base": 500.0,
            "materials": 0.0,
            "equipment": 0.0,
            "total": 500.0
        }

def format_cost_summary(language, length, width, construction_type, materials, equipment):
    """Format cost summary for display."""
    costs = calculate_cost(length, width, construction_type, materials, equipment)
    
    summary = get_text(language, "cost_summary")
    summary += f"{get_text(language, 'base_price')}{costs['base']:.2f}€\n"
    summary += f"{get_text(language, 'materials_cost')}{costs['materials']:.2f}€\n"
    summary += f"{get_text(language, 'equipment_cost')}{costs['equipment']:.2f}€"
    summary += get_text(language, "total_price", total=f"{costs['total']:.2f}")
    
    logger.info(f"📋 SUMMARY FORMATTED:\n{summary}")
    
    return summary

# ============================================================================
# HANDLERS
# ============================================================================

@router.message(Command("start"))
async def cmd_start(message: Message, state: FSMContext) -> None:
    """Start command."""
    logger.info(f"🚀 START COMMAND from user {message.from_user.id}")
    await state.clear()
    await state.set_state(ConfigurationStates.selecting_language)
    await message.answer(
        "Выберите язык / Select language / Izveljieties valodu:",
        reply_markup=get_language_keyboard()
    )

@router.callback_query(F.data.startswith("lang_"))
async def select_language(callback: CallbackQuery, state: FSMContext) -> None:
    """Language selection."""
    language = callback.data.split("_")[1]
    logger.info(f"🌐 LANGUAGE SELECTED: {language}")
    await state.update_data(language=language)
    await callback.message.edit_text(
        get_text(language, "welcome"),
        reply_markup=get_start_keyboard(language)
    )
    await callback.answer()

@router.callback_query(F.data == "open_3d_configurator")
async def open_3d_configurator(callback: CallbackQuery, state: FSMContext) -> None:
    """Open 3D configurator."""
    data = await state.get_data()
    language = data.get("language", "EN")
    
    length = data.get("length", 3)
    width = data.get("width", 3)
    construction = data.get("construction_type", "standard")
    materials = data.get("materials", [])
    equipment = data.get("equipment", [])
    
    kb, url = get_3d_configurator_keyboard(language, length, width, construction, materials, equipment)
    
    message_text = f"{get_text(language, '3d_description')}\n\n🔗 <code>{url}</code>"
    
    await callback.message.edit_text(message_text, reply_markup=kb, parse_mode="HTML")
    await callback.answer()

@router.callback_query(F.data == "start_config")
async def start_configuration(callback: CallbackQuery, state: FSMContext) -> None:
    """Start configuration."""
    data = await state.get_data()
    language = data.get("language", "EN")
    logger.info(f"⚙️ START CONFIGURATION: language={language}")
    await state.set_state(ConfigurationStates.choosing_length)
    await callback.message.edit_text(
        get_text(language, "step_length"),
        reply_markup=get_length_keyboard(language)
    )
    await callback.answer()

@router.callback_query(F.data.startswith("length_"))
async def choose_length(callback: CallbackQuery, state: FSMContext) -> None:
    """Choose length."""
    data = await state.get_data()
    language = data.get("language", "EN")
    length = float(callback.data.split("_")[1])
    logger.info(f"📏 LENGTH SELECTED: {length}м")
    await state.update_data(length=length)
    await state.set_state(ConfigurationStates.choosing_width)
    summary = get_text(language, "selected_length", length=length) + "\n\n"
    summary += get_text(language, "step_width")
    await callback.message.edit_text(summary, reply_markup=get_width_keyboard(language))
    await callback.answer()

@router.callback_query(F.data.startswith("width_"))
async def choose_width(callback: CallbackQuery, state: FSMContext) -> None:
    """Choose width."""
    data = await state.get_data()
    language = data.get("language", "EN")
    width = float(callback.data.split("_")[1])
    logger.info(f"📐 WIDTH SELECTED: {width}м")
    await state.update_data(width=width)
    await state.set_state(ConfigurationStates.choosing_construction_type)
    length = data.get("length", 2.0)
    area = length * width
    summary = get_text(language, "selected_length", length=length) + "\n"
    summary += get_text(language, "selected_width", width=width) + "\n"
    summary += get_text(language, "selected_area", area=area) + "\n\n"
    summary += get_text(language, "step_construction")
    await callback.message.edit_text(summary, reply_markup=get_construction_keyboard(language))
    await callback.answer()

@router.callback_query(F.data.startswith("construction_"))
async def choose_construction(callback: CallbackQuery, state: FSMContext) -> None:
    """Choose construction type."""
    data = await state.get_data()
    language = data.get("language", "EN")
    construction_type = callback.data.split("_")[1]
    logger.info(f"🏗️ CONSTRUCTION SELECTED: {construction_type}")
    construction_name = CONSTRUCTION_TYPES[construction_type].get(f"name_{language.lower()}", CONSTRUCTION_TYPES[construction_type]["name_en"])
    await state.update_data(construction_type=construction_type)
    await state.set_state(ConfigurationStates.choosing_materials)
    length = data.get("length", 2.0)
    width = data.get("width", 2.0)
    area = length * width
    summary = get_text(language, "selected_length", length=length) + "\n"
    summary += get_text(language, "selected_width", width=width) + "\n"
    summary += get_text(language, "selected_area", area=area) + "\n"
    summary += get_text(language, "selected_construction", construction=construction_name) + "\n\n"
    summary += get_text(language, "step_materials")
    await callback.message.edit_text(summary, reply_markup=get_materials_keyboard(language, []))
    await callback.answer()

@router.callback_query(F.data.startswith("material_"))
async def toggle_material(callback: CallbackQuery, state: FSMContext) -> None:
    """Toggle material."""
    data = await state.get_data()
    language = data.get("language", "EN")
    material_key = callback.data.split("_")[1]
    materials = data.get("materials", [])
    if material_key in materials:
        materials.remove(material_key)
        logger.info(f"🗑️ MATERIAL REMOVED: {material_key}")
    else:
        materials.append(material_key)
        logger.info(f"➕ MATERIAL ADDED: {material_key}")
    await state.update_data(materials=materials)
    with suppress(TelegramBadRequest):
        await callback.message.edit_reply_markup(reply_markup=get_materials_keyboard(language, materials))
    await callback.answer()

@router.callback_query(F.data == "materials_done")
async def materials_done(callback: CallbackQuery, state: FSMContext) -> None:
    """Materials done."""
    data = await state.get_data()
    language = data.get("language", "EN")
    logger.info(f"✅ MATERIALS DONE")
    await state.set_state(ConfigurationStates.choosing_equipment)
    length = data.get("length", 2.0)
    width = data.get("width", 2.0)
    area = length * width
    construction_type = data.get("construction_type", "standard")
    construction_name = CONSTRUCTION_TYPES[construction_type].get(f"name_{language.lower()}", CONSTRUCTION_TYPES[construction_type]["name_en"])
    materials = data.get("materials", [])
    materials_text = ", ".join([MATERIALS[m].get(f"name_{language.lower()}", MATERIALS[m]["name_en"]) for m in materials if m in MATERIALS]) or get_text(language, "none_selected")
    summary = get_text(language, "selected_length", length=length) + "\n"
    summary += get_text(language, "selected_width", width=width) + "\n"
    summary += get_text(language, "selected_area", area=area) + "\n"
    summary += get_text(language, "selected_construction", construction=construction_name) + "\n"
    summary += get_text(language, "selected_materials", materials=materials_text) + "\n\n"
    summary += get_text(language, "step_equipment")
    await callback.message.edit_text(summary, reply_markup=get_equipment_keyboard(language, []))
    await callback.answer()

@router.callback_query(F.data.startswith("equipment_"))
async def toggle_equipment(callback: CallbackQuery, state: FSMContext) -> None:
    """Toggle equipment."""
    data = await state.get_data()
    language = data.get("language", "EN")
    equipment_key = callback.data.split("_")[1]
    equipment = data.get("equipment", [])
    if equipment_key in equipment:
        equipment.remove(equipment_key)
        logger.info(f"🗑️ EQUIPMENT REMOVED: {equipment_key}")
    else:
        equipment.append(equipment_key)
        logger.info(f"➕ EQUIPMENT ADDED: {equipment_key}")
    await state.update_data(equipment=equipment)
    with suppress(TelegramBadRequest):
        await callback.message.edit_reply_markup(reply_markup=get_equipment_keyboard(language, equipment))
    await callback.answer()

@router.callback_query(F.data == "equipment_done")
async def equipment_done(callback: CallbackQuery, state: FSMContext) -> None:
    """Equipment done - SEND COST SUMMARY."""
    logger.info("=" * 60)
    logger.info("🎯 EQUIPMENT DONE - STARTING COST CALCULATION")
    logger.info("=" * 60)
    
    data = await state.get_data()
    language = data.get("language", "EN")
    
    length = data.get("length", 2.0)
    width = data.get("width", 2.0)
    construction_type = data.get("construction_type", "standard")
    materials = data.get("materials", [])
    equipment = data.get("equipment", [])
    
    logger.info(f"📊 DATA RECEIVED: length={length}, width={width}, construction={construction_type}, materials={materials}, equipment={equipment}")
    
    summary = format_cost_summary(language, length, width, construction_type, materials, equipment)
    
    logger.info(f"📝 SUMMARY TEXT:\n{summary}")
    logger.info("=" * 60)
    logger.info("📤 SENDING SUMMARY TO TELEGRAM")
    logger.info("=" * 60)
    
    await state.set_state(ConfigurationStates.confirmation)
    
    try:
        await callback.message.edit_text(summary, reply_markup=get_confirmation_keyboard(language))
        logger.info("✅ MESSAGE SENT SUCCESSFULLY via edit_text()")
    except Exception as e:
        logger.error(f"❌ ERROR SENDING MESSAGE via edit_text(): {str(e)}")
        try:
            await callback.message.answer(summary, reply_markup=get_confirmation_keyboard(language))
            logger.info("✅ MESSAGE SENT SUCCESSFULLY via answer()")
        except Exception as e2:
            logger.error(f"❌ ERROR SENDING MESSAGE via answer(): {str(e2)}")
    
    await callback.answer()

@router.callback_query(F.data == "confirm_order")
async def confirm_order(callback: CallbackQuery, state: FSMContext) -> None:
    """Confirm order."""
    data = await state.get_data()
    language = data.get("language", "EN")
    logger.info(f"✅ ORDER CONFIRMED")
    await state.set_state(ConfigurationStates.final_report)
    summary = format_cost_summary(language, data.get("length", 2.0), data.get("width", 2.0), data.get("construction_type", "standard"), data.get("materials", []), data.get("equipment", []))
    final_text = f"{get_text(language, 'order_confirmed')}\n\n{summary}"
    await callback.message.edit_text(final_text, reply_markup=get_final_keyboard(language))
    await callback.answer()

# BACK BUTTONS
@router.callback_query(F.data == "back_to_length")
async def back_to_length(callback: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    language = data.get("language", "EN")
    logger.info("⬅️ BACK TO LENGTH")
    await state.set_state(ConfigurationStates.choosing_length)
    await callback.message.edit_text(get_text(language, "step_length"), reply_markup=get_length_keyboard(language))
    await callback.answer()

@router.callback_query(F.data == "back_to_width")
async def back_to_width(callback: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    language = data.get("language", "EN")
    logger.info("⬅️ BACK TO WIDTH")
    await state.set_state(ConfigurationStates.choosing_width)
    length = data.get("length", 2.0)
    summary = get_text(language, "selected_length", length=length) + "\n\n" + get_text(language, "step_width")
    await callback.message.edit_text(summary, reply_markup=get_width_keyboard(language))
    await callback.answer()

@router.callback_query(F.data == "back_to_construction")
async def back_to_construction(callback: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    language = data.get("language", "EN")
    logger.info("⬅️ BACK TO CONSTRUCTION")
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
    logger.info("⬅️ BACK TO MATERIALS")
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
    logger.info("⬅️ BACK TO EQUIPMENT")
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
    logger.info("❌ CONFIGURATION CANCELED")
    await state.clear()
    await state.update_data(language=language)
    await callback.message.edit_text(get_text(language, "canceled"), reply_markup=get_start_keyboard(language))
    await callback.answer()

@router.callback_query(F.data == "main_menu")
async def main_menu(callback: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    language = data.get("language", "EN")
    logger.info("🏠 MAIN MENU")
    await state.clear()
    await state.update_data(language=language)
    await callback.message.edit_text(get_text(language, "welcome"), reply_markup=get_start_keyboard(language))
    await callback.answer()

# ============================================================================
# MAIN
# ============================================================================

async def main() -> None:
    dp.include_router(router)
    try:
        logger.info("🤖 BOT IS RUNNING AND READY TO WORK...")
        logger.info(f"📍 Configurator URL: {CONFIGURATOR_URL}")
        await dp.start_polling(bot)
    finally:
        await bot.session.close()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
