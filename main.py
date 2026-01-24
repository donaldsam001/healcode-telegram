from typing import Final
from telegram import Update
from telegram.ext import ContextTypes
# from editor.interfaces import EditOptions
import logging
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters

TOKEN: Final ="8542774756:AAFD7Qskm7tdefbsWLoXZgD9cExEZUhaDf8"
BOT_USERNAME: Final = "@healcodebot"

# 2. Command: 
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hello! I'm your HealCode bot. How can I assist you today?")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Please type something and i can respond back to you!")

async def custom_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("This is a custom command response.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message_text: str = update.message.chat.type
    text: str = update.message.text

    print(f'User ({update.massage.chat.id}) in {message_text} sent: {text}')

    user_query = " ".join(context.args)
    if not user_query:
        await update.message.reply_text("Please provide a question. Example: /ask How do I use Zoekt?")
        return

    # Uses the primary LLM (e.g., Gemini) defined in your AIService
    # response = await ai_service.chat(user_query)
    response = "This is a placeholder response from the AI service."
    await update.message.reply_text(f"🤖 AI Response:\n\n{response}")

async def error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f'Update {update} caused error {context.error}')


if __name__ == '__main__':
    # Replace 'YOUR_TOKEN_HERE' with your actual token
    MYTOKEN = '8542774756:AAFD7Qskm7tdefbsWLoXZgD9cExEZUhaDf8'

    print('Starting bot...')
    application = ApplicationBuilder().token(MYTOKEN).build()

    application.add_handler(CommandHandler('start',start_command))
    application.add_handler(CommandHandler('help',help_command))
    application.add_handler(CommandHandler('custom',custom_command))

    application.add_handler(MessageHandler(filters.TEXT,handle_message))

    application.add_error_handler(error)

    print("Polling...")
    application.run_polling(poll_interval=3)

# Assuming ai_service is already initialized in your main bot script
# async def ask_ai(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     user_query = " ".join(context.args)
#     if not user_query:
#         await update.message.reply_text("Please provide a question. Example: /ask How do I use Zoekt?")
#         return

#     # Uses the primary LLM (e.g., Gemini) defined in your AIService
#     response = await ai_service.chat(user_query)
#     await update.message.reply_text(f"🤖 AI Response:\n\n{response}")