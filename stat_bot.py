import os
import re
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import pdfplumber
import io
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN не найден")
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Привет! Отправь мне PDF файл с отчетом Markets Forecast, и я подсчитаю статистику по комнатам."
    )

async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
    document = update.message.document

    # Проверяем, что это PDF файл
    if document.mime_type != "application/pdf":
        await update.message.reply_text("Пожалуйста, отправьте PDF файл.")
        return

    # Скачиваем файл
    file = await context.bot.get_file(document.file_id)
    file_bytes = await file.download_as_bytearray()

    try:
        # Обрабатываем PDF
        result = process_pdf(file_bytes)
        await update.message.reply_text(result)
    except Exception as e:
        await update.message.reply_text(f"Ошибка при обработке файла: {str(e)}")

def process_pdf(file_bytes):
    # Открываем PDF из памяти
    with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
        # Собираем все данные из таблиц
        all_data = {}
        dates = []

        for page in pdf.pages:
            # Извлекаем таблицы
            tables = page.extract_tables()

            for table in tables:
                for i, row in enumerate(table):
                    # Пропускаем пустые строки и заголовки
                    if not row or not row[0] or row[0] in ['Market Code', '']:
                        continue

                    market_code = row[0].strip()

                    # Если это строка с датами (первая строка с числами)
                    if market_code.isdigit() and not dates:
                        dates = [cell for cell in row[1:] if cell]
                        continue

                    # Если это market code
                    if market_code in ['AF', 'CI', 'CT', 'CY', 'PK', 'TA', 'TB', 'TC', 'TE', 'TF', 'TG', 'TZ', 'ZZ',
                                       'CK', 'CL', 'TD', 'PB', 'PC', 'PI', 'PL', 'PJ', 'TH', 'CJ', 'CS']:
                        if market_code not in all_data:
                            all_data[market_code] = []

                        # Извлекаем значения комнат
                        room_values = []
                        for cell in row[1:]:
                            if cell is not None and cell != '':
                                # Убираем нечисловые символы и преобразуем в int
                                clean_cell = re.sub(r'[^\d]', '', str(cell))
                                if clean_cell.isdigit():
                                    room_values.append(int(clean_cell))
                                else:
                                    room_values.append(0)
                            else:
                                room_values.append(0)

                        all_data[market_code].extend(room_values)

        # Удаляем последний день месяца из данных (последний столбец)
        for market_code in all_data:
            if all_data[market_code]:
                all_data[market_code] = all_data[market_code][:-1]

        # Определяем количество дней в месяце (по самой длинной существующей категории)
        max_days = 0
        for market_code in all_data:
            if all_data[market_code] and len(all_data[market_code]) > max_days:
                max_days = len(all_data[market_code])

        # Если не нашли данных, используем 31 день по умолчанию
        if max_days == 0:
            max_days = 31

        # Формируем результат
        result = "Статистика по комнатам:\n\n"

        # Public Individual Direct Full: TA
        ta_values = all_data.get('TA', [])
        # Если данных нет, заполняем нулями
        if not ta_values:
            ta_values = [0] * max_days
        result += f"Public Individual Direct Full: {' '.join(map(str, ta_values))}\n\n"

        # Public Individual Direct Disc: TB+TC+TD+PB+PC+PI+PL+PJ+PK+TZ
        tb_values = all_data.get('TB', [])
        tc_values = all_data.get('TC', [])
        td_values = all_data.get('TD', [])
        pb_values = all_data.get('PB', [])
        pc_values = all_data.get('PC', [])
        pi_values = all_data.get('PI', [])
        pl_values = all_data.get('PL', [])
        pj_values = all_data.get('PJ', [])
        pk_values = all_data.get('PK', [])
        tz_values = all_data.get('TZ', [])

        # Объединяем значения (добавляем нули если списки разной длины)
        max_len = max(
            len(tb_values) if tb_values else 0,
            len(tc_values) if tc_values else 0,
            len(td_values) if td_values else 0,
            len(pb_values) if pb_values else 0,
            len(pc_values) if pc_values else 0,
            len(pi_values) if pi_values else 0,
            len(pl_values) if pl_values else 0,
            len(pj_values) if pj_values else 0,
            len(pk_values) if pk_values else 0,
            len(tz_values) if tz_values else 0,
            max_days  # Добавляем max_days для случаев, когда все списки пустые
        )

        direct_disc_values = []
        for i in range(max_len):
            total = 0
            if tb_values and i < len(tb_values): total += tb_values[i]
            if tc_values and i < len(tc_values): total += tc_values[i]
            if td_values and i < len(td_values): total += td_values[i]
            if pb_values and i < len(pb_values): total += pb_values[i]
            if pc_values and i < len(pc_values): total += pc_values[i]
            if pi_values and i < len(pi_values): total += pi_values[i]
            if pl_values and i < len(pl_values): total += pl_values[i]
            if pj_values and i < len(pj_values): total += pj_values[i]
            if pk_values and i < len(pk_values): total += pk_values[i]
            if tz_values and i < len(tz_values): total += tz_values[i]
            direct_disc_values.append(total)

        result += f"Public Individual Direct Disc: {' '.join(map(str, direct_disc_values))}\n\n"

        # Public Individual Indirect Full: TE
        te_values = all_data.get('TE', [])
        if not te_values:
            te_values = [0] * max_days
        result += f"Public Individual Indirect Full: {' '.join(map(str, te_values))}\n\n"

        # Public Individual Indirect Disc: TF+TG+TH
        tf_values = all_data.get('TF', [])
        tg_values = all_data.get('TG', [])
        th_values = all_data.get('TH', [])

        max_len = max(
            len(tf_values) if tf_values else 0,
            len(tg_values) if tg_values else 0,
            len(th_values) if th_values else 0,
            max_days  # Добавляем max_days для случаев, когда все списки пустые
        )
        indirect_disc_values = []
        for i in range(max_len):
            total = 0
            if tf_values and i < len(tf_values): total += tf_values[i]
            if tg_values and i < len(tg_values): total += tg_values[i]
            if th_values and i < len(th_values): total += th_values[i]
            indirect_disc_values.append(total)

        result += f"Public Individual Indirect Disc: {' '.join(map(str, indirect_disc_values))}\n\n"

        # Corporate Individual: CI+CJ
        ci_values = all_data.get('CI', [])
        cj_values = all_data.get('CJ', [])

        max_len = max(
            len(ci_values) if ci_values else 0,
            len(cj_values) if cj_values else 0,
            max_days  # Добавляем max_days для случаев, когда все списки пустые
        )
        corporate_values = []
        for i in range(max_len):
            total = 0
            if ci_values and i < len(ci_values): total += ci_values[i]
            if cj_values and i < len(cj_values): total += cj_values[i]
            corporate_values.append(total)

        result += f"Corporate Individual: {' '.join(map(str, corporate_values))}\n\n"

        # Travel Agency Individual: CK+CL
        ck_values = all_data.get('CK', [])
        cl_values = all_data.get('CL', [])

        max_len = max(
            len(ck_values) if ck_values else 0,
            len(cl_values) if cl_values else 0,
            max_days  # Добавляем max_days для случаев, когда все списки пустые
        )
        travel_agency_values = []
        for i in range(max_len):
            total = 0
            if ck_values and i < len(ck_values): total += ck_values[i]
            if cl_values and i < len(cl_values): total += cl_values[i]
            travel_agency_values.append(total)

        result += f"Travel Agency Individual: {' '.join(map(str, travel_agency_values))}\n\n"

        # Business Group: AF+CS
        af_values = all_data.get('AF', [])
        cs_values = all_data.get('CS', [])

        max_len = max(
            len(af_values) if af_values else 0,
            len(cs_values) if cs_values else 0,
            max_days  # Добавляем max_days для случаев, когда все списки пустые
        )
        business_group_values = []
        for i in range(max_len):
            total = 0
            if af_values and i < len(af_values): total += af_values[i]
            if cs_values and i < len(cs_values): total += cs_values[i]
            business_group_values.append(total)

        result += f"Business Group: {' '.join(map(str, business_group_values))}\n\n"

        # Leisure Group: CT
        ct_values = all_data.get('CT', [])
        if not ct_values:
            ct_values = [0] * max_days
        result += f"Leisure Group: {' '.join(map(str, ct_values))}\n\n"

        # Airlines: CY
        cy_values = all_data.get('CY', [])
        if not cy_values:
            cy_values = [0] * max_days
        result += f"Airlines: {' '.join(map(str, cy_values))}"

        return result


def main():
    # Создаем приложение
    application = Application.builder().token(BOT_TOKEN).build()

    # Добавляем обработчики
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.Document.ALL, handle_document))

    # Запускаем бота
    print("Бот запущен...")
    application.run_polling()


if __name__ == "__main__":
    main()