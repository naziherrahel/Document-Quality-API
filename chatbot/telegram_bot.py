# import logging
# import requests
# from telegram import Update
# from telegram.ext import (
#     Application,
#     CommandHandler,
#     MessageHandler,
#     filters,
#     ContextTypes,
# )
# from telegram.constants import ParseMode
# from datetime import datetime

# # Configure logging
# logging.basicConfig(
#     format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
#     level=logging.INFO,
# )
# logger = logging.getLogger(__name__)

# # FastAPI server URL
# API_URL = "http://localhost:8000/batch-quality-assessment/"
# BOT_TOKEN = "7852032398:AAGFoTXNtWBs-rQQQlUIfdIMPoBTcQkofaQ"

# async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
#     """Handle the /start command with Russian message."""
#     await update.message.reply_text(
#         "Добро пожаловать в бот для загрузки документов! Пожалуйста, загрузите один или несколько документов (например, паспорт, миграционная карта) в виде высококачественного скана или PDF."
#     )

# async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
#     """Handle document uploads (PDFs, images) and send to the FastAPI batch quality assessment endpoint."""
#     documents = []
    
#     if update.message.document:
#         documents = [update.message.document]
#     elif update.message.photo:
#         documents = [update.message.photo[-1]]
#     else:
#         await update.message.reply_text("Пожалуйста, загрузите действительный документ (PDF или изображение).")
#         return

#     files = []
#     for doc in documents:
#         try:
#             file = await doc.get_file()
#             if update.message.document:
#                 file_name = doc.file_name or f"document_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
#                 mime_type = doc.mime_type or "application/octet-stream"
#             else:
#                 file_name = f"photo_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
#                 mime_type = "image/jpeg"

#             file_bytes = await file.download_as_bytearray()
#             files.append(("files", (file_name, file_bytes, mime_type)))
#             logger.info(f"Received file: {file_name} from user {update.message.from_user.id}")
#         except Exception as e:
#             logger.error(f"Error processing file: {str(e)}")
#             await update.message.reply_text(
#                 f"Ошибка при обработке файла. Пожалуйста, попробуйте снова."
#             )
#             return

#     try:
#         response = requests.post(API_URL, files=files, timeout=120)
#         if response.status_code == 200:
#             results = response.json()
#             messages = ["📄 Документы обработаны:"]

#             doc_counter = 1
#             for result in results:
#                 filename = result["filename"]
#                 if result["error"]:
#                     messages.append(
#                         f"❌ Ошибка при обработке файла '{filename}': {result['error']}."
#                     )
#                     continue

#                 doc_results = result.get("result", [])
#                 if not doc_results:
#                     messages.append(
#                         f"⚠️ В файле '{filename}' не найдены документы. Загрузите высококачественный скан."
#                     )
#                     continue

#                 for doc_result in doc_results:
#                     doc_type = doc_result.get("doc_type", "unknown")
#                     quality_category = doc_result.get("quality_category", "unknown")

#                     doc_type_ru = {
#                         "passport": "Паспорт",
#                         "registration": "Регистрация",
#                         "children": "Детский документ",
#                         "inn": "ИНН",
#                         "snils": "СНИЛС",
#                         "migration": "Миграционная карта",
#                         "unknown": "Неизвестный документ"
#                     }.get(doc_type.lower(), doc_type)

#                     if quality_category.lower() == "failed":
#                         messages.append(
#                             f"⚠️ Документ {doc_counter} ({doc_type_ru}) не распознан. Загрузите высококачественный скан."
#                         )
#                     else:
#                         messages.append(
#                             f"✅ Документ {doc_counter} ({doc_type_ru}) успешно обработан."
#                         )
#                     doc_counter += 1

#             if len(messages) == 1:  # Only header, no documents
#                 messages.append("⚠️ Документы не найдены. Загрузите высококачественный скан.")
#             await update.message.reply_text("\n".join(messages), parse_mode=ParseMode.MARKDOWN)
#         else:
#             logger.error(f"API error: {response.status_code} - {response.text}")
#             await update.message.reply_text(
#                 "Извините, произошла ошибка при обработке ваших документов. Пожалуйста, попробуйте снова позже."
#             )

#     except Exception as e:
#         logger.error(f"Error processing documents: {str(e)}", exc_info=True)
#         await update.message.reply_text(
#             "Произошла ошибка при обработке ваших документов. Пожалуйста, попробуйте снова."
#         )

# async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
#     """Log errors caused by updates."""
#     logger.error(f"Update {update} caused error {context.error}")

# def main() -> None:
#     """Run the bot."""
#     application = Application.builder().token(BOT_TOKEN).build()

#     application.add_handler(CommandHandler("start", start))
#     application.add_handler(MessageHandler(filters.Document.ALL | filters.PHOTO, handle_document))
#     application.add_error_handler(error_handler)

#     logger.info("Starting Telegram bot...")
#     application.run_polling(allowed_updates=Update.ALL_TYPES)

# if __name__ == "__main__":
#     main()


# import logging
# import requests
# from telegram import Update
# from telegram.ext import (
#     Application,
#     CommandHandler,
#     MessageHandler,
#     filters,
#     ContextTypes,
# )
# from telegram.constants import ParseMode
# from datetime import datetime

# logging.basicConfig(
#     format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
#     level=logging.INFO,
# )
# logger = logging.getLogger(__name__)

# API_URL = "http://localhost:8000/batch-quality-assessment/"
# BOT_TOKEN = "7852032398:AAGFoTXNtWBs-rQQQlUIfdIMPoBTcQkofaQ"

# async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
#     """Handle the /start command with Russian message."""
#     await update.message.reply_text(
#         "Добро пожаловать в бот для загрузки документов! Пожалуйста, загрузите один или несколько документов (например, паспорт, миграционная карта) в виде высококачественного скана или PDF."
#     )

# async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
#     """Handle document uploads (PDFs, images) and send to the FastAPI batch quality assessment endpoint."""
#     documents = []
    
#     if update.message.document:
#         documents = [update.message.document]
#     elif update.message.photo:
#         documents = [update.message.photo[-1]]
#     else:
#         await update.message.reply_text("Пожалуйста, загрузите действительный документ (PDF или изображение).")
#         return

#     files = []
#     for doc in documents:
#         try:
#             file = await doc.get_file()
#             if update.message.document:
#                 file_name = doc.file_name or f"document_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
#                 mime_type = doc.mime_type or "application/octet-stream"
#             else:
#                 file_name = f"photo_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
#                 mime_type = "image/jpeg"

#             file_bytes = await file.download_as_bytearray()
#             files.append(("files", (file_name, file_bytes, mime_type)))
#             logger.info(f"Received file: {file_name} from user {update.message.from_user.id}")
#         except Exception as e:
#             logger.error(f"Error processing file: {str(e)}")
#             await update.message.reply_text(
#                 f"Ошибка при обработке файла. Пожалуйста, попробуйте снова."
#             )
#             return

#     try:
#         response = requests.post(API_URL, files=files, timeout=120)
#         if response.status_code == 200:
#             results = response.json()
#             messages = ["📄 Документы обработаны:"]

#             doc_counter = 1
#             reupload_prompt = False
#             for result in results:
#                 filename = result["filename"]
#                 if result["error"]:
#                     messages.append(
#                         f"❌ Ошибка при обработке файла '{filename}': {result['error']}."
#                     )
#                     reupload_prompt = True
#                     continue

#                 doc_results = result.get("result", [])
#                 if not doc_results:
#                     messages.append(
#                         f"⚠️ В файле '{filename}' не найдены документы. Загрузите высококачественный скан."
#                     )
#                     reupload_prompt = True
#                     continue

#                 if result.get("reupload_required", False):
#                     reupload_prompt = True

#                 for doc_result in doc_results:
#                     doc_type = doc_result.get("doc_type", "unknown")
#                     quality_category = doc_result.get("quality_category", "unknown")

#                     doc_type_ru = {
#                         "passport": "Паспорт",
#                         "registration": "Регистрация",
#                         "children": "Детский документ",
#                         "inn": "ИНН",
#                         "snils": "СНИЛС",
#                         "migration": "Миграционная карта",
#                         "unknown": "Неизвестный документ"
#                     }.get(doc_type.lower(), doc_type)

#                     if quality_category.lower() in ["failed", "poor"]:
#                         messages.append(
#                             f"⚠️ Документ {doc_counter} ({doc_type_ru}) имеет низкое качество ({quality_category}). Пожалуйста, загрузите высококачественный скан."
#                         )
#                     else:
#                         messages.append(
#                             f"✅ Документ {doc_counter} ({doc_type_ru}) успешно обработан, качество: {quality_category}."
#                         )
#                     doc_counter += 1

#             if reupload_prompt:
#                 messages.append("📎 Пожалуйста, загрузите документы с более высоким качеством для точной обработки.")

#             if len(messages) == 1:  # Only header, no documents
#                 messages.append("⚠️ Документы не найдены. Загрузите высококачественный скан.")
#             await update.message.reply_text("\n".join(messages), parse_mode=ParseMode.MARKDOWN)
#         else:
#             logger.error(f"API error: {response.status_code} - {response.text}")
#             await update.message.reply_text(
#                 "Извините, произошла ошибка при обработке ваших документов. Пожалуйста, попробуйте снова позже."
#             )

#     except Exception as e:
#         logger.error(f"Error processing documents: {str(e)}", exc_info=True)
#         await update.message.reply_text(
#             "Произошла ошибка при обработке ваших документов. Пожалуйста, попробуйте снова."
#         )

# async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
#     """Log errors caused by updates."""
#     logger.error(f"Update {update} caused error {context.error}")

# def main() -> None:
#     """Run the bot."""
#     application = Application.builder().token(BOT_TOKEN).build()

#     application.add_handler(CommandHandler("start", start))
#     application.add_handler(MessageHandler(filters.Document.ALL | filters.PHOTO, handle_document))
#     application.add_error_handler(error_handler)

#     logger.info("Starting Telegram bot...")
#     application.run_polling(allowed_updates=Update.ALL_TYPES)

# if __name__ == "__main__":
#     main()


# import logging
# import requests
# from telegram import Update
# from telegram.ext import (
#     Application,
#     CommandHandler,
#     MessageHandler,
#     filters,
#     ContextTypes,
# )
# from telegram.constants import ParseMode

# # Configure logging
# logging.basicConfig(
#     format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
#     level=logging.INFO,
# )
# logger = logging.getLogger(__name__)

# # FastAPI server URL
# API_URL = "http://localhost:8000/batch-quality-assessment/"
# BOT_TOKEN = "7852032398:AAGFoTXNtWBs-rQQQlUIfdIMPoBTcQkofaQ"

# async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
#     """Handle the /start command with Russian message."""
#     await update.message.reply_text(
#         "Добро пожаловать в бот для загрузки документов! Пожалуйста, загрузите один или несколько документов (например, паспорт, резюме)."
#     )

# async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
#     """Handle document uploads (single or multiple) and send to the FastAPI batch quality assessment endpoint."""
#     documents = []
    
#     if update.message.document:
#         documents = [update.message.document]
#     elif update.message.photo:
#         documents = [update.message.photo[-1]]
#     else:
#         await update.message.reply_text("Пожалуйста, загрузите действительный документ или изображение.")
#         return

#     files = []
#     for doc in documents:
#         try:
#             file = await doc.get_file()
#             if update.message.document:
#                 file_name = doc.file_name or f"document_{file.file_id}"
#                 mime_type = doc.mime_type or "application/octet-stream"
#             else:
#                 file_name = f"photo_{file.file_id}.jpg"
#                 mime_type = "image/jpeg"

#             file_bytes = await file.download_as_bytearray()
#             files.append(("files", (file_name, file_bytes, mime_type)))
#             logger.info(f"Received file: {file_name} from user {update.message.from_user.id}")
#         except Exception as e:
#             logger.error(f"Error processing file: {str(e)}")
#             await update.message.reply_text(
#                 f"Ошибка при обработке файла. Пожалуйста, попробуйте снова."
#             )
#             return

#     try:
#         response = requests.post(API_URL, files=files, timeout=60)
#         if response.status_code == 200:
#             results = response.json()
#             messages = []
#             for result in results:
#                 filename = result["filename"]
#                 if result["error"]:
#                     messages.append(
#                         f"❌ Ошибка при обработке файла '{filename}': {result['error']}. Пожалуйста, попробуйте снова."
#                     )
#                     continue

#                 doc_results = result["result"]
#                 if not doc_results:
#                     messages.append(
#                         f"⚠️ Файл '{filename}' не содержит распознанных документов."
#                     )
#                     continue

#                 for idx, doc_result in enumerate(doc_results, 1):
#                     doc_type = doc_result["doc_type"]
#                     quality_category = doc_result["quality_category"]

#                     doc_type_ru = {
#                         "passport": "Паспорт",
#                         "resume": "Резюме",
#                         "id_card": "Удостоверение личности",
#                         "unknown": f"{filename} (Документ {idx})"
#                     }.get(doc_type.lower(), doc_type)

#                     if quality_category.lower() == "failed":
#                         messages.append(
#                             f"⚠️ Документ {idx} ('{doc_type_ru}') в файле '{filename}' не распознан. Пожалуйста, загрузите более четкую версию."
#                         )
#                     elif quality_category.lower() in ["excellent", "moderate"]:
#                         messages.append(
#                             f"✅ Документ {idx} ('{doc_type_ru}') в файле '{filename}' успешно загружен."
#                         )
#                     else:
#                         messages.append(
#                             f"⚠️ Документ {idx} ('{doc_type_ru}') в файле '{filename}' имеет низкое качество. Пожалуйста, загрузите более четкую версию."
#                         )

#             await update.message.reply_text("\n".join(messages), parse_mode=ParseMode.MARKDOWN)
#         else:
#             logger.error(f"API error: {response.status_code} - {response.text}")
#             await update.message.reply_text(
#                 "Извините, произошла ошибка при обработке ваших документов. Пожалуйста, попробуйте снова позже."
#             )

#     except Exception as e:
#         logger.error(f"Error processing documents: {str(e)}", exc_info=True)
#         await update.message.reply_text(
#             "Произошла ошибка при обработке ваших документов. Пожалуйста, попробуйте снова."
#         )

# async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
#     """Log errors caused by updates."""
#     logger.error(f"Update {update} caused error {context.error}")

# def main() -> None:
#     """Run the bot."""
#     application = Application.builder().token(BOT_TOKEN).build()

#     application.add_handler(CommandHandler("start", start))
#     application.add_handler(MessageHandler(filters.Document.ALL | filters.PHOTO, handle_document))
#     application.add_error_handler(error_handler)

#     logger.info("Starting Telegram bot...")
#     application.run_polling(allowed_updates=Update.ALL_TYPES)

# if __name__ == "__main__":
#     main()



# import logging
# import requests
# from telegram import Update
# from telegram.ext import (
#     Application,
#     CommandHandler,
#     MessageHandler,
#     filters,
#     ContextTypes,
# )
# from telegram.constants import ParseMode
# from datetime import datetime

# # Configure logging
# logging.basicConfig(
#     format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
#     level=logging.INFO,
# )
# logger = logging.getLogger(__name__)

# # FastAPI server URL
# API_URL = "http://localhost:8000/batch-quality-assessment/"
# BOT_TOKEN = "7852032398:AAGFoTXNtWBs-rQQQlUIfdIMPoBTcQkofaQ"

# async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
#     """Handle the /start command with Russian message."""
#     await update.message.reply_text(
#         "Добро пожаловать в бот для загрузки документов! Пожалуйста, загрузите один или несколько документов (например, паспорт, резюме) в виде высококачественного скана."
#     )

# async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
#     """Handle document uploads (single or multiple) and send to the FastAPI batch quality assessment endpoint."""
#     documents = []
    
#     if update.message.document:
#         documents = [update.message.document]
#     elif update.message.photo:
#         documents = [update.message.photo[-1]]
#     else:
#         await update.message.reply_text("Пожалуйста, загрузите действительный документ или изображение.")
#         return

#     files = []
#     for doc in documents:
#         try:
#             file = await doc.get_file()
#             if update.message.document:
#                 file_name = doc.file_name or f"document_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
#                 mime_type = doc.mime_type or "application/octet-stream"
#             else:
#                 file_name = f"photo_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
#                 mime_type = "image/jpeg"

#             file_bytes = await file.download_as_bytearray()
#             files.append(("files", (file_name, file_bytes, mime_type)))
#             logger.info(f"Received file: {file_name} from user {update.message.from_user.id}")
#         except Exception as e:
#             logger.error(f"Error processing file: {str(e)}")
#             await update.message.reply_text(
#                 f"Ошибка при обработке файла. Пожалуйста, попробуйте снова."
#             )
#             return

#     try:
#         response = requests.post(API_URL, files=files, timeout=60)
#         if response.status_code == 200:
#             results = response.json()
#             messages = []
#             for result in results:
#                 filename = result["filename"]
#                 if result["error"]:
#                     messages.append(
#                         f"❌ Ошибка при обработке файла '{filename}': {result['error']}."
#                     )
#                     continue

#                 doc_results = result.get("result", [])
#                 if not doc_results:
#                     messages.append(
#                         f"⚠️ В файле '{filename}' не найдены документы. Пожалуйста, загрузите высококачественный скан документа (например, с помощью сканера, а не камеры телефона)."
#                     )
#                     continue

#                 for idx, doc_result in enumerate(doc_results, 1):
#                     doc_type = doc_result.get("doc_type", "unknown")
#                     quality_category = doc_result.get("quality_category", "unknown")

#                     doc_type_ru = {
#                         "passport": "Паспорт",
#                         "resume": "Резюме",
#                         "id_card": "Удостоверение личности",
#                         "migration": "Миграционная карта",
#                         "unknown": f"Документ {idx}"
#                     }.get(doc_type.lower(), doc_type)

#                     if quality_category.lower() == "failed":
#                         messages.append(
#                             f"⚠️ Документ {idx} ({doc_type_ru}) не распознан. Загрузите высококачественный скан документа."
#                         )
#                     elif quality_category.lower() in ["excellent", "moderate"]:
#                         messages.append(
#                             f"✅ Документ {idx} ({doc_type_ru}) успешно обработан."
#                         )
#                     else:
#                         messages.append(
#                             f"⚠️ Документ {idx} ({doc_type_ru}) имеет низкое качество. Загрузите высококачественный скан документа."
#                         )

#             await update.message.reply_text("\n".join(messages), parse_mode=ParseMode.MARKDOWN)
#         else:
#             logger.error(f"API error: {response.status_code} - {response.text}")
#             await update.message.reply_text(
#                 "Извините, произошла ошибка при обработке ваших документов. Пожалуйста, попробуйте снова позже."
#             )

#     except Exception as e:
#         logger.error(f"Error processing documents: {str(e)}", exc_info=True)
#         await update.message.reply_text(
#             "Произошла ошибка при обработке ваших документов. Пожалуйста, попробуйте снова."
#         )

# async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
#     """Log errors caused by updates."""
#     logger.error(f"Update {update} caused error {context.error}")

# def main() -> None:
#     """Run the bot."""
#     application = Application.builder().token(BOT_TOKEN).build()

#     application.add_handler(CommandHandler("start", start))
#     application.add_handler(MessageHandler(filters.Document.ALL | filters.PHOTO, handle_document))
#     application.add_error_handler(error_handler)

#     logger.info("Starting Telegram bot...")
#     application.run_polling(allowed_updates=Update.ALL_TYPES)

# if __name__ == "__main__":
#     main()
import logging
import requests
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
)
from telegram.constants import ParseMode
from datetime import datetime

# Configure logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# FastAPI server URL
API_URL = "http://localhost:8000/batch-quality-assessment/"
BOT_TOKEN = "7852032398:AAGFoTXNtWBs-rQQQlUIfdIMPoBTcQkofaQ"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /start command with Russian message."""
    await update.message.reply_text(
        "Добро пожаловать в бот для загрузки документов! Пожалуйста, загрузите один или несколько документов (например, паспорт, резюме) в виде высококачественного скана или PDF."
    )

async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle document uploads (PDFs, images) and send to the FastAPI batch quality assessment endpoint."""
    documents = []
    
    if update.message.document:
        documents = [update.message.document]
    elif update.message.photo:
        documents = [update.message.photo[-1]]
    else:
        await update.message.reply_text("Пожалуйста, загрузите действительный документ (PDF или изображение).")
        return

    files = []
    for doc in documents:
        try:
            file = await doc.get_file()
            if update.message.document:
                file_name = doc.file_name or f"document_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
                mime_type = doc.mime_type or "application/octet-stream"
            else:
                file_name = f"photo_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
                mime_type = "image/jpeg"

            file_bytes = await file.download_as_bytearray()
            files.append(("files", (file_name, file_bytes, mime_type)))
            logger.info(f"Received file: {file_name} from user {update.message.from_user.id}")
        except Exception as e:
            logger.error(f"Error processing file: {str(e)}")
            await update.message.reply_text(
                f"Ошибка при обработке файла. Пожалуйста, попробуйте снова."
            )
            return

    try:
        response = requests.post(API_URL, files=files, timeout=120)
        if response.status_code == 200:
            results = response.json()
            messages = []
            for result in results:
                filename = result["filename"]
                if result["error"]:
                    messages.append(
                        f"❌ Ошибка при обработке файла '{filename}': {result['error']}."
                    )
                    continue

                doc_results = result.get("result", [])
                # Extract page number for PDFs
                page_info = ""
                if "_page" in filename:
                    page_num = filename.split("_page")[1].split(".")[0]
                    page_info = f" (Страница {page_num})"

                if not doc_results:
                    messages.append(
                        f"⚠️ В файле '{filename}'{page_info} не найдены документы. Пожалуйста, загрузите высококачественный скан документа (например, с помощью сканера, а не камеры телефона)."
                    )
                    continue

                for idx, doc_result in enumerate(doc_results, 1):
                    doc_type = doc_result.get("doc_type", "unknown")
                    quality_category = doc_result.get("quality_category", "unknown")

                    doc_type_ru = {
                        "passport": "Паспорт",
                        "resume": "Резюме",
                        "id_card": "Удостоверение личности",
                        "migration": "Миграционная карта",
                        "unknown": f"Документ {idx}"
                    }.get(doc_type.lower(), doc_type)

                    if quality_category.lower() == "failed":
                        messages.append(
                            f"⚠️ Документ {idx} ({doc_type_ru}){page_info} не распознан. Загрузите высококачественный скан документа."
                        )
                    elif quality_category.lower() in ["excellent", "moderate"]:
                        messages.append(
                            f"✅ Документ {idx} ({doc_type_ru}){page_info} успешно обработан."
                        )
                    else:
                        messages.append(
                            f"⚠️ Документ {idx} ({doc_type_ru}){page_info} имеет низкое качество. Загрузите высококачественный скан документа."
                        )

            await update.message.reply_text("\n".join(messages), parse_mode=ParseMode.MARKDOWN)
        else:
            logger.error(f"API error: {response.status_code} - {response.text}")
            await update.message.reply_text(
                "Извините, произошла ошибка при обработке ваших документов. Пожалуйста, попробуйте снова позже."
            )

    except Exception as e:
        logger.error(f"Error processing documents: {str(e)}", exc_info=True)
        await update.message.reply_text(
            "Произошла ошибка при обработке ваших документов. Пожалуйста, попробуйте снова."
        )

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Log errors caused by updates."""
    logger.error(f"Update {update} caused error {context.error}")

def main() -> None:
    """Run the bot."""
    application = Application.builder().token(BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.Document.ALL | filters.PHOTO, handle_document))
    application.add_error_handler(error_handler)

    logger.info("Starting Telegram bot...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()