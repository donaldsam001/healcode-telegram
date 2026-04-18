import os
import json
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from healcode_api import *
# Import toàn bộ hàm từ file healcode_api mới
from healcode_api import (
    call_credential_create,
    get_list_repo,
    add_repo,
    switch_branch,
    get_git_status,
    call_fix_api,
    call_cancel_fix,
    get_queue_stats,
    get_all_tasks
)

# Load environment variables from .env.local
load_dotenv('.env.local')
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
API_AUTH_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1dWlkIjoiNDAyNDNlNWMtYjQzMS00ZDY4LWJjYjItZTliZjB" \
"iMTEwMzE5IiwiZXhwIjoxODA3NjA0MzAwfQ.4JAiTbBJhvatwB7FzeutmfbYmYMy03tAzl-VovGKTUY" # Token này dùng để gọi API


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    username = update.effective_user.username or "User"
    print(f"Username: {username}")

    # Khởi tạo profile
    result = call_credential_create(username=username, provider_id="telegram")
    print("API Result:", result)

    menu_text = (
        f"Hello {username}!\n\n"
        "🤖 **Healcode Bot Ready!**\n"
        "I can help you analyze, refactor, and manage your code repositories.\n\n"
        
        "Danh sách các lệnh hỗ trợ:\n"
        "🔹 `/list` - Xem danh sách Repositories\n"
        "🔹 `/repo <url> [branch]` - Thêm/Clone một repo mới\n"
        "🔹 `/branches <branch_name>` - Đổi nhánh làm việc (Git checkout)\n"
        "🔹 `/cursor` - Xem vị trí/trạng thái Git hiện tại\n"
        "🔹 `/fix <mô_tả_lỗi>` - Yêu cầu AI sửa lỗi\n"
        "🔹 `/cancel <request_id>` - Hủy tiến trình fix\n"
        "🔹 `/status` - Xem trạng thái hệ thống/hàng đợi\n"
    )
    await update.message.reply_text(menu_text, parse_mode='Markdown')

async def list_repo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🔄 Đang lấy danh sách repository...")
    
    result = get_list_repo(auth_token=API_AUTH_TOKEN)
    
    # Kiểm tra nếu API trả về lỗi
    if isinstance(result, dict) and "error" in result:
        await update.message.reply_text(f"❌ Lỗi: {result['error']}")
        return

    msg = "📂 **Danh sách Repository của bạn:**\n\n"
    # Giả định API trả về list
    if isinstance(result, list):
        if not result:
            msg += "📭 Chưa có repository nào."
        else:
            for r in result:
                msg += f"📦 `{r}`\n"
    else:
        # Nếu backend trả về JSON stringified Object
        msg += f"```json\n{json.dumps(result, indent=2)}\n```"
        
    await update.message.reply_text(msg, parse_mode='Markdown')

async def repo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("⚠️ Vui lòng nhập đường dẫn repo.\nVí dụ: `/repo https://github.com/user/repo.git main`", parse_mode='Markdown')
        return

    repo_url = context.args[0]
    branch = context.args[1] if len(context.args) > 1 else "main"

    await update.message.reply_text(f"📥 Đang clone/thiết lập repo `{repo_url}` (Nhánh: `{branch}`)...", parse_mode='Markdown')
    
    result = add_repo(url=repo_url, branch=branch, auth_token=API_AUTH_TOKEN)

    if isinstance(result, dict) and "error" in result:
        msg = f"❌ **Lỗi:** {result['error']}"
    else:
        msg = f"✅ **Phản hồi từ hệ thống:**\n```json\n{json.dumps(result, indent=2)}\n```"

    await update.message.reply_text(msg, parse_mode='Markdown')

async def branches(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("⚠️ Vui lòng nhập tên branch muốn đổi.\nVí dụ: `/branches feature-login`", parse_mode='Markdown')
        return

    branch_name = context.args[0]
    await update.message.reply_text(f"🌿 Đang yêu cầu chuyển sang nhánh `{branch_name}`...", parse_mode='Markdown')

    result = switch_branch(branch=branch_name, auth_token=API_AUTH_TOKEN)
    
    if isinstance(result, dict) and "error" in result:
        msg = f"❌ **Lỗi:** {result['error']}"
    else:
        msg = f"🔄 **Phản hồi:**\n```json\n{json.dumps(result, indent=2)}\n```"

    await update.message.reply_text(msg, parse_mode='Markdown')

async def cursor(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🔍 Đang truy xuất trạng thái Git hiện tại của bạn...")
    
    result = get_git_status(auth_token=API_AUTH_TOKEN)
    
    if isinstance(result, dict) and "error" in result:
        msg = f"❌ **Lỗi:** {result['error']}"
    else:
        msg = f"📍 **Vị trí/Trạng thái hiện tại:**\n```json\n{json.dumps(result, indent=2)}\n```"

    await update.message.reply_text(msg, parse_mode='Markdown')

async def fix(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Lệnh fix mới không cần repo_name nữa
    if not context.args:
        await update.message.reply_text("⚠️ Cú pháp: `/fix <mô_tả_lỗi>`\nVí dụ: `/fix IndexError at line 10 in main.py`", parse_mode='Markdown')
        return

    # Nối tất cả các từ thành chuỗi lỗi
    issue = " ".join(context.args)

    await update.message.reply_text(f"🛠 Đang gửi yêu cầu phân tích và sửa lỗi...\n📝 **Trace:** `{issue}`", parse_mode='Markdown')

    result = call_fix_api(trace_error=issue, auth_token=API_AUTH_TOKEN)

    if isinstance(result, dict) and "error" in result:
        msg = f"❌ **Lỗi:** {result.get('error')}"
    elif "detail" in result: # Lỗi Validation (422)
        msg = f"❌ **Validation Error:** {result['detail']}"
    else:
        # Nếu thành công
        msg = f"✅ **Đã nhận yêu cầu Fix!**\n```json\n{json.dumps(result, indent=2)}\n```"

    await update.message.reply_text(msg, parse_mode='Markdown')

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("⚠️ Cú pháp: `/cancel <request_id>`\nVí dụ: `/cancel req_12345`", parse_mode='Markdown')
        return

    request_id = context.args[0]

    await update.message.reply_text(f"🛑 Đang gửi yêu cầu hủy task `{request_id}`...", parse_mode='Markdown')

    result = call_cancel_fix(request_id=request_id, auth_token=API_AUTH_TOKEN)

    if isinstance(result, dict) and "error" in result:
        msg = f"❌ **Lỗi:** {result['error']}"
    else:
        msg = f"✅ **Kết quả Hủy:**\n```json\n{json.dumps(result, indent=2)}\n```"

    await update.message.reply_text(msg, parse_mode='Markdown')

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🔄 Checking status...")

    # Gọi API thống kê
    stats_result = get_git_status(auth_token=API_AUTH_TOKEN)
    
    # Tùy chọn: Bạn có thể gọi thêm get_all_tasks() nếu muốn hiển thị chi tiết
    # tasks_result = get_all_tasks(auth_token=API_AUTH_TOKEN)

    if isinstance(stats_result, dict) and "error" in stats_result:
        msg = f"❌ Lỗi khi lấy trạng thái: {stats_result['error']}"
    else:
        msg = f"📊 **System Queue Stats:**\n```json\n{json.dumps(stats_result, indent=2)}\n```"

    await update.message.reply_text(msg, parse_mode='Markdown')


if __name__ == "__main__":
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
    
    # Đăng ký các handler
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("list", list_repo))
    app.add_handler(CommandHandler("repo", repo))
    app.add_handler(CommandHandler("branches", branches))
    app.add_handler(CommandHandler("cursor", cursor))
    app.add_handler(CommandHandler("fix", fix))
    app.add_handler(CommandHandler("cancel", cancel))
    app.add_handler(CommandHandler("status", status))
    
    print("🤖 Bot đang chạy...")
    app.run_polling()