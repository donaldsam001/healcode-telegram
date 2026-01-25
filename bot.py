import os
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from healcode_api import call_healcode_api

# Load environment variables from .env.local
load_dotenv('.env.local')

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if not context.args:
        await update.message.reply_text("Nhập token github")
        return

    token = context.args[0]

    fake_code = f"authenticate({token}) {{}}"

    username = f"user_{token[:10]}"  # Giả sử username được tạo từ token


    menu_text = (
        "Hello " + username + "!\n\n"
        "🤖 **Healcode Bot Ready!**\n"
        "I can help you analyze, refactor, and manage your code repositories. "
        "If you're new to the workflow, please see the documentation.\n\n"
        
        "You can control the pipeline by sending these commands:\n\n"
        "/repo link\n"
        "/fix (issue or none for all)\n"
        "/cancel \n"
        "/status \n\n"
    )

    await update.message.reply_text(menu_text)

async def repo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # 1. Kiểm tra xem người dùng có nhập tham số không (context.args có rỗng không)
    if not context.args:
        await update.message.reply_text("⚠️ Vui lòng nhập đường dẫn repo.\nVí dụ: /repo https://github.com/username/project.git your_token")
        return

    # 2. Lấy tham số đầu tiên (chính là link repo người dùng nhập)
    repo_url = context.args[0]

    token = context.args[1]

    # 3. Xử lý logic với tham số vừa nhận được
    # (Ví dụ: Tạo payload code dựa trên repo_url để gửi đi)
    fake_code = f"pull repo({repo_url}, {token}) {{}}" 
    
    # Gọi API với tham số thực tế
    result = call_healcode_api(fake_code)

    msg = f"🧠 Healcode Result cho repo {repo_url}:\n"
    
    # Kiểm tra xem API có trả về suggestions không để tránh lỗi
    if "suggestions" in result:
        for s in result["suggestions"]:
            msg += f"• {s}\n"
    else:
        msg += "Không tìm thấy gợi ý nào hoặc có lỗi xảy ra."

    await update.message.reply_text(msg)

async def fix(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # 1. Kiểm tra tham số TRƯỚC khi gán để tránh lỗi IndexError
    if context.args:
        # Lấy tham số người dùng nhập (ví dụ: /fix bug_login -> issue = "bug_login")
        issue = context.args[0] 
    else:
        # Nếu không nhập gì, gán mặc định là "all"
        issue = "all"
        await update.message.reply_text("⚠️ Bạn chưa nhập vấn đề, hệ thống sẽ sửa tất cả (default: all).")

    # 2. Thêm chữ 'f' vào trước chuỗi để nhận biến {issue}
    # Lưu ý: Cần nhân đôi dấu ngoặc nhọn {{}} nếu muốn giữ lại dấu ngoặc trong string kết quả
    fake_code = f"fix code({issue}) {{}}"
    
    # Gọi API
    result = call_healcode_api(fake_code)

    msg = "🧠 Healcode Result:\n"
    
    # Kiểm tra result để tránh lỗi nếu API trả về null/None
    if result:
        for s in result:
            # Giả sử result là dictionary: {"file.py": "fixed content"}
            msg += f"• {s}: {result[s]}\n"
    else:
        msg += "Không có dữ liệu trả về."

    await update.message.reply_text(msg)

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Cancelling operation...")

    fake_code = "cancel() {}"
    result = call_healcode_api(fake_code)

    msg = "🧠 Healcode Result:\n"
    for s in result["suggestions"]:
        msg += f"• {s}\n"

    await update.message.reply_text(msg)

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Checking status...")

    fake_code = "status() {}"
    result = call_healcode_api(fake_code)

    msg = "🧠 Healcode Result:\n"
    for s in result["suggestions"]:
        msg += f"• {s}\n"

    await update.message.reply_text(msg)

# Get the token from environment variable
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')

if not TELEGRAM_BOT_TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN not found in .env.local file")

app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("repo", repo))
app.add_handler(CommandHandler("fix", fix))
app.add_handler(CommandHandler("cancel", cancel))
app.add_handler(CommandHandler("status", status))
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