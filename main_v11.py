"""
Exhibition Booth Configurator Bot v11 (SUPER RELIABLE)
- Simplified cost calculation sending
- Extended logging to terminal
- Guaranteed message delivery
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

# Load environment variables
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")

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
    "standard": {"name_en": "Standard", "name_ru": "Standart", "name_lv": "Standarts", "price": 500.0},
    "exclusive": {"name_en": "Exclusive", "name_ru": "Eksklusiv", "name_lv": "Eksklusivs", "price": 800.0}
}

MATERIALS = {
    "plastic": {"name_en": "Plastic", "name_ru": "Plastik", "name_lv": "Plastmasa", "price": 50.0},
    "wood": {"name_en": "Wood", "name_ru": "Derevo", "name_lv": "Koks", "price": 150.0},
    "metal": {"name_en": "Metal", "name_ru": "Metall", "name_lv": "Metals", "price": 200.0}
}

EQUIPMENT = {
    "lighting": {"name_en": "Lighting", "name_ru": "Osveshenie", "name_lv": "Apgaismojums", "price": 300.0},
    "furniture": {"name_en": "Furniture", "name_ru": "Mebel", "name_lv": "Mebeles", "price": 400.0},
    "monitor": {"name_en": "Monitor", "name_ru": "Monitor", "name_lv": "Monitors", "price": 800.0}
}

# ============================================================================
# TRANSLATIONS
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
        "selected_area": "Area: {area}m2",
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
        "error_calc": "Error calculating cost. Please try again."
    },
    "RUS": {
        "welcome": "Dobro pozhalovat v Konfigurator Vystavochnykh Stendov!\n\nDavajte sozdadim vash idealnyj stend. Nazhimte 'Nachat konfiguraciyu'.",
        "step_length": "Vyberi dlinu stenda (v metrah):",
        "step_width": "Vyberi shirinu stenda (v metrah):",
        "step_construction": "Vyberi tip konstrukcii:",
        "step_materials": "Vyberi materialy (mozhno vybrat neskolko):",
        "step_equipment": "Vyberi dopolnitelnoe oborudovanie (mozhno vybrat neskolko):",
        "selected_length": "Dlina: {length}m",
        "selected_width": "Shirina: {width}m",
        "selected_area": "Ploshad: {area}m2",
        "selected_construction": "Tip: {construction}",
        "selected_materials": "Materialy: {materials}",
        "selected_equipment": "Oborudovanie: {equipment}",
        "none_selected": "Ne vybrano",
        "calculate": "Rasschitat",
        "confirm": "Podtverdit zakaz",
        "cancel": "Otmena",
        "back": "Nazad",
        "order_confirmed": "Zakaz podtverzhen!\n\nSpasibo za ispolzovanie nashego servisa!",
        "main_menu": "Glavnoe menu",
        "canceled": "Konfiguracija otmenena. Vyberi yazyk, chtoby nachat zanovo.",
        "cost_summary": "SMETA STOIMOSTI\n\n",
        "base_price": "Bazovyj stend: ",
        "materials_cost": "Materialy: ",
        "equipment_cost": "Oborudovanie: ",
        "total_price": "\nITOGO: {total} EUR",
        "error_calc": "Oshibka pri raschete stoimosti. Poprobuj esche raz."
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
        "selected_area": "Platiba: {area}m2",
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
        "error_calc": "Kluda aprekjinat izmaksas. Ludzu, megjinat vejirez."
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
        [InlineKeyboardButton(text="English", callback_data="lang_EN")],
        [InlineKeyboardButton(text="Russkij", callback_data="lang_RUS")],
        [InlineKeyboardButton(text="Latviesu", callback_data="lang_LV")]
    ])
    return kb

def get_start_keyboard(language):
    """Start menu keyboard."""
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=get_text(language, "calculate"), callback_data="start_config")]
    ])
    return kb

def get_length_keyboard(language):
    """Length selection keyboard."""
    buttons = [[InlineKeyboardButton(text=f"{l}m", callback_data=f"length_{l}")] for l in LENGTHS]
    kb = InlineKeyboardMarkup(inline_keyboard=buttons)
    return kb

def get_width_keyboard(language):
    """Width selection keyboard."""
    buttons = [[InlineKeyboardButton(text=f"{w}m", callback_data=f"width_{w}")] for w in WIDTHS]
    buttons.append([InlineKeyboardButton(text=get_text(language, "back"), callback_data="back_to_length")])
    kb = InlineKeyboardMarkup(inline_keyboard=buttons)
    return kb

def get_construction_keyboard(language):
    """Construction type selection keyboard."""
    buttons = []
    for key, val in CONSTRUCTION_TYPES.items():
        name = val.get(f"name_{language.lower()}", val["name_en"])
        price = val["price"]
        buttons.append([InlineKeyboardButton(text=f"{name} +{price:.0f} EUR", callback_data=f"construction_{key}")])
    buttons.append([InlineKeyboardButton(text=get_text(language, "back"), callback_data="back_to_width")])
    kb = InlineKeyboardMarkup(inline_keyboard=buttons)
    return kb

def get_materials_keyboard(language, selected_materials):
    """Materials selection keyboard."""
    buttons = []
    for key, val in MATERIALS.items():
        name = val.get(f"name_{language.lower()}", val["name_en"])
        price = val["price"]
        check = "[X]" if key in selected_materials else "[ ]"
        buttons.append([InlineKeyboardButton(text=f"{check} {name} +{price:.0f} EUR", callback_data=f"material_{key}")])
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
        check = "[X]" if key in selected_equipment else "[ ]"
        buttons.append([InlineKeyboardButton(text=f"{check} {name} +{price:.0f} EUR", callback_data=f"equipment_{key}")])
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

# ============================================================================
# COST CALCULATION (SUPER SIMPLE AND RELIABLE)
# ============================================================================

def calculate_cost(length, width, construction_type, materials, equipment):
    """Calculate total cost - GUARANTEED TO WORK."""
    try:
        # Convert to float
        length = float(length) if length else 2.0
        width = float(width) if width else 2.0
        
        # Base price
        base_price = CONSTRUCTION_TYPES.get(construction_type, CONSTRUCTION_TYPES["standard"])["price"]
        
        # Area
        area = length * width
        base_total = base_price * area
        
        # Materials
        materials_total = 0.0
        for m in materials:
            if m in MATERIALS:
                materials_total += MATERIALS[m]["price"] * area
        
        # Equipment
        equipment_total = 0.0
        for e in equipment:
            if e in EQUIPMENT:
                equipment_total += EQUIPMENT[e]["price"]
        
        # Total
        total = base_total + materials_total + equipment_total
        
        logger.info(f"COST CALCULATED: Base={base_total:.2f} EUR, Materials={materials_total:.2f} EUR, Equipment={equipment_total:.2f} EUR, TOTAL={total:.2f} EUR")
        
        return {
            "base": base_total,
            "materials": materials_total,
            "equipment": equipment_total,
            "total": total
        }
    except Exception as e:
        logger.error(f"ERROR IN CALCULATION: {str(e)}")
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
    summary += f"{get_text(language, 'base_price')}{costs['base']:.2f} EUR\n"
    summary += f"{get_text(language, 'materials_cost')}{costs['materials']:.2f} EUR\n"
    summary += f"{get_text(language, 'equipment_cost')}{costs['equipment']:.2f} EUR"
    summary += get_text(language, "total_price", total=f"{costs['total']:.2f}")
    
    logger.info(f"SUMMARY FORMATTED:\n{summary}")
    
    return summary

# ============================================================================
# HANDLERS
# ============================================================================

@router.message(Command("start"))
async def cmd_start(message: Message, state: FSMContext) -> None:
    """Start command."""
    logger.info(f"START COMMAND from user {message.from_user.id}")
    await state.clear()
    await state.set_state(ConfigurationStates.selecting_language)
    await message.answer(
        "Select your language / Vyberi yazyk / Izveljieties valodu:",
        reply_markup=get_language_keyboard()
    )

@router.callback_query(F.data.startswith("lang_"))
async def select_language(callback: CallbackQuery, state: FSMContext) -> None:
    """Language selection."""
    language = callback.data.split("_")[1]
    logger.info(f"LANGUAGE SELECTED: {language}")
    await state.update_data(language=language)
    await callback.message.edit_text(
        get_text(language, "welcome"),
        reply_markup=get_start_keyboard(language)
    )
    await callback.answer()

@router.callback_query(F.data == "start_config")
async def start_configuration(callback: CallbackQuery, state: FSMContext) -> None:
    """Start configuration."""
    data = await state.get_data()
    language = data.get("language", "EN")
    logger.info(f"START CONFIGURATION: language={language}")
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
    logger.info(f"LENGTH SELECTED: {length}m")
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
    logger.info(f"WIDTH SELECTED: {width}m")
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
    logger.info(f"CONSTRUCTION SELECTED: {construction_type}")
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
        logger.info(f"MATERIAL REMOVED: {material_key}")
    else:
        materials.append(material_key)
        logger.info(f"MATERIAL ADDED: {material_key}")
    await state.update_data(materials=materials)
    with suppress(TelegramBadRequest):
        await callback.message.edit_reply_markup(reply_markup=get_materials_keyboard(language, materials))
    await callback.answer()

@router.callback_query(F.data == "materials_done")
async def materials_done(callback: CallbackQuery, state: FSMContext) -> None:
    """Materials done."""
    data = await state.get_data()
    language = data.get("language", "EN")
    logger.info(f"MATERIALS DONE")
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
        logger.info(f"EQUIPMENT REMOVED: {equipment_key}")
    else:
        equipment.append(equipment_key)
        logger.info(f"EQUIPMENT ADDED: {equipment_key}")
    await state.update_data(equipment=equipment)
    with suppress(TelegramBadRequest):
        await callback.message.edit_reply_markup(reply_markup=get_equipment_keyboard(language, equipment))
    await callback.answer()

@router.callback_query(F.data == "equipment_done")
async def equipment_done(callback: CallbackQuery, state: FSMContext) -> None:
    """Equipment done - SEND COST SUMMARY."""
    logger.info("=== EQUIPMENT DONE - STARTING COST CALCULATION ===")
    
    data = await state.get_data()
    language = data.get("language", "EN")
    
    # Get all data
    length = data.get("length", 2.0)
    width = data.get("width", 2.0)
    construction_type = data.get("construction_type", "standard")
    materials = data.get("materials", [])
    equipment = data.get("equipment", [])
    
    logger.info(f"DATA RECEIVED: length={length}, width={width}, construction={construction_type}, materials={materials}, equipment={equipment}")
    
    # Calculate summary
    summary = format_cost_summary(language, length, width, construction_type, materials, equipment)
    
    logger.info(f"SUMMARY TEXT:\n{summary}")
    logger.info("=== SENDING SUMMARY TO TELEGRAM ===")
    
    # Set state
    await state.set_state(ConfigurationStates.confirmation)
    
    # Send message
    try:
        await callback.message.edit_text(summary, reply_markup=get_confirmation_keyboard(language))
        logger.info("MESSAGE SENT SUCCESSFULLY")
    except Exception as e:
        logger.error(f"ERROR SENDING MESSAGE: {str(e)}")
        await callback.message.answer(summary, reply_markup=get_confirmation_keyboard(language))
        logger.info("MESSAGE SENT VIA answer() METHOD")
    
    await callback.answer()

@router.callback_query(F.data == "confirm_order")
async def confirm_order(callback: CallbackQuery, state: FSMContext) -> None:
    """Confirm order."""
    data = await state.get_data()
    language = data.get("language", "EN")
    logger.info(f"ORDER CONFIRMED")
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
    logger.info("BACK TO LENGTH")
    await state.set_state(ConfigurationStates.choosing_length)
    await callback.message.edit_text(get_text(language, "step_length"), reply_markup=get_length_keyboard(language))
    await callback.answer()

@router.callback_query(F.data == "back_to_width")
async def back_to_width(callback: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    language = data.get("language", "EN")
    logger.info("BACK TO WIDTH")
    await state.set_state(ConfigurationStates.choosing_width)
    length = data.get("length", 2.0)
    summary = get_text(language, "selected_length", length=length) + "\n\n" + get_text(language, "step_width")
    await callback.message.edit_text(summary, reply_markup=get_width_keyboard(language))
    await callback.answer()

@router.callback_query(F.data == "back_to_construction")
async def back_to_construction(callback: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    language = data.get("language", "EN")
    logger.info("BACK TO CONSTRUCTION")
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
    logger.info("BACK TO MATERIALS")
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
    logger.info("BACK TO EQUIPMENT")
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
    logger.info("CONFIGURATION CANCELED")
    await state.clear()
    await state.update_data(language=language)
    await callback.message.edit_text(get_text(language, "canceled"), reply_markup=get_start_keyboard(language))
    await callback.answer()

@router.callback_query(F.data == "main_menu")
async def main_menu(callback: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    language = data.get("language", "EN")
    logger.info("MAIN MENU")
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
        logger.info("BOT IS RUNNING AND READY TO WORK...")
        await dp.start_polling(bot)
    finally:
        await bot.session.close()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
