import os
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from healcode_api import *


# Load environment variables from .env.local
load_dotenv('.env.local')

# done
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    id = update.effective_user.id
    username = update.effective_user.username
    print("Username:", username)
    if not context.args:
        await update.message.reply_text("Nhập token github")
        return
    token = context.args[0]
    print("token:", token)
    result = call_start_api(str(id), username, token)
    print("API Result:", result)

    menu_text = (
        "Hello "  + username + "!\n\n"
        "🤖 **Healcode Bot Ready!**\n"
        "I can help you analyze, refactor, and manage your code repositories. "
        "If you're new to the workflow, please see the documentation.\n\n"
        
        "You can control the pipeline by sending these commands:\n\n"
        "/list (get all repos)\n"
        "/repo link\n"
        "/branch name\n"
        "/cursor \n"
        "/fix (issue or none for all)\n"
        "/cancel \n"
        "/status \n\n"
    )

    await update.message.reply_text(menu_text)

async def list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    pass

async def repo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # 1. Kiểm tra xem người dùng có nhập tham số không (context.args có rỗng không)
    if not context.args:
        await update.message.reply_text("⚠️ Vui lòng nhập đường dẫn repo.\nVí dụ: /repo https://github.com/username/project.git your_token")
        return

    # 2. Lấy tham số đầu tiên (chính là link repo người dùng nhập)
    repo_url = context.args[0]

    if len(context.args) < 2:
        await update.message.reply_text("⚠️ Vui lòng nhập branch.\n")
    branch = context.args[1]

    # 3. Xử lý logic với tham số vừa nhận được
    # (Ví dụ: Tạo payload code dựa trên repo_url để gửi đi)
    
    # Gọi API với tham số thực tế
    result = call_repo_api(repo_url, branch)

    msg = f"🧠 Healcode Result cho repo {repo_url}:\n"
    
    # Kiểm tra xem API có trả về suggestions không để tránh lỗi
    if "suggestions" in result:
        for s in result["suggestions"]:
            msg += f"• {s}\n"
    else:
        msg += "Không tìm thấy gợi ý nào hoặc có lỗi xảy ra."

    await update.message.reply_text(msg)

async def branch(update: Update, context: ContextTypes.DEFAULT_TYPE):
    pass

async def cursor(update: Update, context: ContextTypes.DEFAULT_TYPE):
    pass

async def fix(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Cần: Tên repo (để tạo path URL) và lỗi (trace error)
    if len(context.args) < 2:
        await update.message.reply_text("⚠️ Cú pháp: /fix <tên_repo> <mô_tả_lỗi>\nVí dụ: /fix my-project 'IndexError at line 10'")
        return

    repo_name = context.args[0]
    # Nối tất cả các từ còn lại thành chuỗi lỗi
    issue = " ".join(context.args[1:])

    await update.message.reply_text(f"🛠 Đang gửi yêu cầu fix cho repo `{repo_name}`...")

    result = call_fix_api(repo_name, issue)

    # Backend trả về FixResponseModel (request_id, status, message...)
    if "request_id" in result:
        msg = (
            f"✅ **Đã nhận yêu cầu!**\n"
            f"🆔 ID: `{result['request_id']}`\n"
            f"📌 Trạng thái: {result['status']}\n"
            f"📝 Message: {result['message']}"
        )
    else:
        msg = f"❌ Lỗi: {result.get('detail') or result.get('error')}"

    await update.message.reply_text(msg)

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Cancelling operation...")

    if context.args:
        request = context.args[0] 
    else:
        request = "all"
        await update.message.reply_text("(default: all).")

    result = call_cancel_api(request)

    msg = "🧠 Healcode Result:\n"
    for s in result["suggestions"]:
        msg += f"• {s}\n"

    await update.message.reply_text(msg)

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # API status của backend lấy toàn bộ repo, không cần tham số url/token từ user
    await update.message.reply_text("🔄 Checking system status...")

    result = call_status_api()

    # Backend trả về: {"count": n, "repos": [...], "storage_root": ...}
    if "repos" in result:
        repos = result["repos"]
        if not repos:
            msg = "📭 Chưa có repository nào trong hệ thống."
        else:
            msg = f"📊 **System Status ({result.get('count', 0)} repos):**\n\n"
            for r in repos:
                # r = {"name": "...", "status": "...", "path": "..."}
                msg += f"📦 **Repo:** `{r['name']}`\n   Trạng thái: {r['status']}\n\n"
    else:
        msg = f"❌ Lỗi khi lấy trạng thái: {result}"

    await update.message.reply_text(msg)

# Get the token from environment variable
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')

if not TELEGRAM_BOT_TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN not found in .env.local file")

app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("repo", list))  
app.add_handler(CommandHandler("repo", repo))
app.add_handler(CommandHandler("repo", branch))  
app.add_handler(CommandHandler("repo", cursor))  
app.add_handler(CommandHandler("fix", fix))
app.add_handler(CommandHandler("cancel", cancel))
app.add_handler(CommandHandler("status", status))
app.run_polling()
