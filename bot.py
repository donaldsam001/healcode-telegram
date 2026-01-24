import os
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from healcode_api import call_healcode_api

# Load environment variables from .env.local
load_dotenv('.env.local')

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    menu_text = (
        "🤖 **Healcode Bot Ready!**\n"
        "I can help you analyze, refactor, and manage your code repositories. "
        "If you're new to the workflow, please see the documentation.\n\n"
        
        "You can control the pipeline by sending these commands:\n\n"
        
        "**1. Request Handling & Parsing (API Layer)**\n"
        "/analyze - Start the improvement workflow\n"
        "/permissions - Check chat and user authentication\n"
        "/validate - Test JSON schema for requests\n\n"
        
        "**2. Code Search & Context (Code Management)**\n"
        "/search - Manually trigger Zoekt code search\n"
        "/context - View current local repository snippets\n\n"
        
        "**3. AI & Refactoring Logic (AI Processing)**\n"
        "/explain - Get a summary of the last AI operation\n"
        "/refactor - Direct AI command for current file\n\n"
        
        "**4. Quality & Formatting (Code Quality)**\n"
        "/lint - Run ESLint and Prettier on the workspace\n"
        "/verify - Check for remaining syntax errors\n\n"
        
        "**5. Git & PR Operations (Git Integration)**\n"
        "/branch - Create a new feature branch\n"
        "/commit - Commit and push local changes\n"
        "/pr - Submit a Pull Request to GitHub\n\n"
        
        "**6. Status & Monitoring (Storage & Utils)**\n"
        "/status - View real-time processing logs\n"
        "/errors - View the last failure report\n"
        "/mockdata - Test the API with dummy data"
    )

    await update.message.reply_text(menu_text)

async def analyze(update: Update, context: ContextTypes.DEFAULT_TYPE):
    fake_code = "function test() {}"
    result = call_healcode_api(fake_code)

    msg = "🧠 Healcode Result:\n"
    for s in result["suggestions"]:
        msg += f"• {s}\n"

    await update.message.reply_text(msg)

async def mockdata(update: Update, context: ContextTypes.DEFAULT_TYPE):
    fake_code = "health"
    result = call_healcode_api(fake_code)

    msg = "🧠 Healcode Result:\n"
    for s in result:
        msg += f"• {s}: {result[s]}\n"

    await update.message.reply_text(msg)


# Get the token from environment variable
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')

if not TELEGRAM_BOT_TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN not found in .env.local file")

app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("analyze", analyze))
app.add_handler(CommandHandler("mockdata", mockdata))
# app.add_handler(CommandHandler("repo", repo))  # when implemented
app.run_polling()



# import logging
# from telegram import Update
# from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters

# # 1. Setup logging (crucial for debugging)
# logging.basicConfig(
#     format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
#     level=logging.INFO
# )

# # 2. Command: /start
# async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     await context.bot.send_message(
#         chat_id=update.effective_chat.id, 
#         text="I'm a bot, talk to me!"
#     )

# # 3. Echo handler: Repeats what you say
# async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     await context.bot.send_message(
#         chat_id=update.effective_chat.id, 
#         text=f"You said: {update.message.text}"
#     )

# if __name__ == '__main__':
#     # Replace 'YOUR_TOKEN_HERE' with your actual token
#     MYTOKEN = '8542774756:AAFD7Qskm7tdefbsWLoXZgD9cExEZUhaDf8'
#     application = ApplicationBuilder().token(MYTOKEN).build()
    
#     # Register handlers
#     start_handler = CommandHandler('start', start)
#     echo_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), echo)
    
#     application.add_handler(start_handler)
#     application.add_handler(echo_handler)
    
#     # Start the bot (Polling mode)
#     print("Bot is running...")
#     application.run_polling()