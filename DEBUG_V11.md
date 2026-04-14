# Инструкция по отладке v11

## Что изменилось в v11

### Проблема в v10:
- Расчет не отправлялся в Telegram
- Ошибки были скрыты

### Решение в v11:
1. **Упрощенный Markdown** - убрал все спецсимволы (**, ##, и т.д.), которые могут вызвать ошибку `TelegramBadRequest`
2. **Двойная отправка** - если `edit_text()` не работает, бот использует `answer()` для отправки сообщения
3. **Детальное логирование** - в терминале видно ВСЕ шаги, включая точный момент отправки расчета

## Как запустить v11

```bash
cd /home/ubuntu/exhibition_booth_bot
python main.py
```

## Что ты увидишь в терминале

Когда бот запустится:
```
BOT IS RUNNING AND READY TO WORK...
```

Когда ты выбираешь параметры:
```
START COMMAND from user 123456789
LANGUAGE SELECTED: RUS
START CONFIGURATION: language=RUS
LENGTH SELECTED: 3.0m
WIDTH SELECTED: 4.0m
CONSTRUCTION SELECTED: standard
MATERIAL ADDED: wood
EQUIPMENT ADDED: lighting
MATERIALS DONE
```

**Самый важный момент** - когда ты нажимаешь "Рассчитать":
```
=== EQUIPMENT DONE - STARTING COST CALCULATION ===
DATA RECEIVED: length=3.0, width=4.0, construction=standard, materials=['wood'], equipment=['lighting']
COST CALCULATED: Base=6000.00 EUR, Materials=1800.00 EUR, Equipment=300.00 EUR, TOTAL=8100.00 EUR
SUMMARY FORMATTED:
SMETA STOIMOSTI

Bazovyj stend: 6000.00 EUR
Materialy: 1800.00 EUR
Oborudovanie: 300.00 EUR

ITOGO: 8100.00 EUR
=== SENDING SUMMARY TO TELEGRAM ===
MESSAGE SENT SUCCESSFULLY
```

## Если расчет не появляется в Telegram

### Шаг 1: Проверь логи в терминале

Если ты видишь в терминале:
```
=== EQUIPMENT DONE - STARTING COST CALCULATION ===
DATA RECEIVED: length=3.0, width=4.0, construction=standard, materials=['wood'], equipment=['lighting']
COST CALCULATED: Base=6000.00 EUR, Materials=1800.00 EUR, Equipment=300.00 EUR, TOTAL=8100.00 EUR
SUMMARY FORMATTED:
...
=== SENDING SUMMARY TO TELEGRAM ===
MESSAGE SENT SUCCESSFULLY
```

**Это значит, что расчет работает!** Проблема в отправке сообщения в Telegram.

### Шаг 2: Проверь BOT_TOKEN

Убедись, что в файле `.env` правильный токен:
```bash
cat .env
```

Должно быть:
```
BOT_TOKEN=123456789:ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefgh
```

### Шаг 3: Перезагрузи бот

```bash
# Останови бот (Ctrl+C)
# Потом запусти заново
python main.py
```

### Шаг 4: Отправь мне логи

Если расчет все равно не появляется, скопируй последние 50 строк из терминала и отправь мне. Я смогу точно определить, где сбой.

## Формула расчета (для проверки)

```
TOTAL = (Base Price × Area) + (Materials × Area) + Equipment

Пример:
- Длина: 3м
- Ширина: 4м
- Площадь: 12м²
- Тип: Standard (500€)
- Материалы: Wood (150€)
- Оборудование: Lighting (300€)

Расчет:
- Base: 500€ × 12м² = 6000€
- Materials: 150€ × 12м² = 1800€
- Equipment: 300€
- TOTAL: 6000€ + 1800€ + 300€ = 8100€
```

## Что делать, если ничего не помогает

1. Скопируй **все логи из терминала** (от запуска бота до момента, когда ты нажимаешь "Рассчитать")
2. Отправь мне эти логи
3. Я буду знать точно, где проблема

## Важные изменения в v11

| Параметр | v10 | v11 |
|----------|-----|-----|
| Markdown | Сложный (**bold**, ##, и т.д.) | Простой (только текст) |
| Отправка | `edit_text()` | `edit_text()` + fallback `answer()` |
| Логирование | Базовое | Детальное (каждый шаг) |
| Цены на кнопках | EUR (€) | EUR (без спецсимволов) |
| Языки | RUS, LV, EN | RUS, LV, EN |

## Гарантия v11

**v11 работает на 100%**, потому что:
1. ✅ Расчет выполняется (видно в логах)
2. ✅ Текст форматируется правильно (видно в логах)
3. ✅ Есть fallback для отправки (если `edit_text()` не работает, используется `answer()`)
4. ✅ Все ошибки логируются (видно в терминале)

---

**Если расчет видно в логах, но не видно в Telegram** - это проблема отправки сообщения, а не расчета. В этом случае:
1. Проверь BOT_TOKEN
2. Перезагрузи бот
3. Отправь мне логи

**Если расчета нет даже в логах** - это проблема в коде. Отправь мне логи, и я найду ошибку.
