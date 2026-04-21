import asyncio
import json
import os
from typing import Dict, Optional

from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

from auth_token import Database
from client import HealCodeClient


load_dotenv()
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

db = Database()
user_clients: Dict[int, HealCodeClient] = {}


async def remove_client(user_id: int):
    user_clients.pop(int(user_id), None)


def _extract_token(payload: dict) -> Optional[str]:
    if not isinstance(payload, dict):
        return None
    for key in ("auth_token", "token", "access_token", "jwt"):
        value = payload.get(key)
        if value:
            return value
    data = payload.get("data")
    if isinstance(data, dict):
        for key in ("auth_token", "token", "access_token", "jwt"):
            value = data.get(key)
            if value:
                return value
    return None


async def _build_client(user_id: int) -> HealCodeClient:
    client = await HealCodeClient.create(user_id, db)
    client.set_invalidation_callback(remove_client)
    return client


async def _get_or_restore_client(user_id: int) -> Optional[HealCodeClient]:
    client = user_clients.get(user_id)
    if client and client.is_valid:
        return client
    if client and not client.is_valid:
        await remove_client(user_id)

    restored_client = await _build_client(user_id)
    if not restored_client.api_auth_token:
        return None

    user_clients[user_id] = restored_client
    return restored_client


def _is_unauthorized(result: dict) -> bool:
    if not isinstance(result, dict):
        return False
    return result.get("status_code") == 401 or str(result.get("error", "")).lower() == "unauthorized"


async def _require_client(update: Update) -> Optional[HealCodeClient]:
    user = update.effective_user
    if user is None:
        return None

    client = await _get_or_restore_client(user.id)
    if client:
        return client

    await update.message.reply_text(
        "❌ Chua tim thay phien dang nhap. Vui long chay `/start` de khoi tao lai.",
        parse_mode="Markdown",
    )
    return None


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if user is None:
        return

    user_id = user.id
    username = user.username or str(user_id)
    client = await _build_client(user_id)

    credential_result = await client.credential_create(username=username, provider_id="telegram")
    token = _extract_token(credential_result)
    if token:
        await client.set_token(token)

    user_clients[user_id] = client

    menu_text = (
        f"Hello {username}!\n\n"
        "Healcode Bot Ready.\n\n"
        "Danh sach lenh ho tro:\n"
        "`/list` - Xem danh sach Repositories\n"
        "`/repo <url> [branch]` - Them/Clone mot repo moi\n"
        "`/branches <branch_name>` - Doi nhanh lam viec\n"
        "`/cursor` - Xem trang thai Git hien tai\n"
        "`/fix <mo_ta_loi>` - Yeu cau AI sua loi\n"
        "`/cancel <request_id>` - Huy tien trinh fix\n"
        "`/status` - Xem trang thai he thong\n"
    )

    if _is_unauthorized(credential_result):
        menu_text += "\nCan xac thuc lai. Vui long chay `/start` lai sau."
    elif isinstance(credential_result, dict) and "error" in credential_result and not token:
        menu_text += f"\nBackend tra ve loi: `{credential_result.get('error')}`"

    await update.message.reply_text(menu_text, parse_mode="Markdown")


async def list_repo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    client = await _require_client(update)
    if not client:
        return

    await update.message.reply_text("Dang lay danh sach repository...")
    result = await client.get_list_repo()

    if _is_unauthorized(result):
        await update.message.reply_text("❌ Session het han. Vui long chay `/start` de tao session moi.", parse_mode="Markdown")
        return
    if isinstance(result, dict) and "error" in result:
        await update.message.reply_text(f"❌ Loi: {result['error']}")
        return

    msg = "Danh sach Repository cua ban:\n\n"
    if isinstance(result, list):
        if not result:
            msg += "Chua co repository nao."
        else:
            for repo_item in result:
                msg += f"- `{repo_item}`\n"
    else:
        msg += f"```json\n{json.dumps(result, indent=2)}\n```"

    await update.message.reply_text(msg, parse_mode="Markdown")


async def repo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    client = await _require_client(update)
    if not client:
        return
    if not context.args:
        await update.message.reply_text(
            "Cau lenh: `/repo https://github.com/user/repo.git main`",
            parse_mode="Markdown",
        )
        return

    repo_url = context.args[0]
    branch = context.args[1] if len(context.args) > 1 else "main"
    await update.message.reply_text(f"Dang clone repo `{repo_url}` (branch `{branch}`)...", parse_mode="Markdown")

    result = await client.add_repo(url=repo_url, branch=branch)
    if _is_unauthorized(result):
        await update.message.reply_text("❌ Session het han. Vui long chay `/start` de tao session moi.", parse_mode="Markdown")
        return

    if isinstance(result, dict) and "error" in result:
        msg = f"❌ Loi: {result['error']}"
    else:
        msg = f"✅ Phan hoi:\n```json\n{json.dumps(result, indent=2)}\n```"
    await update.message.reply_text(msg, parse_mode="Markdown")


async def branches(update: Update, context: ContextTypes.DEFAULT_TYPE):
    client = await _require_client(update)
    if not client:
        return
    if not context.args:
        await update.message.reply_text("Cau lenh: `/branches feature-login`", parse_mode="Markdown")
        return

    branch_name = context.args[0]
    await update.message.reply_text(f"Dang chuyen sang branch `{branch_name}`...", parse_mode="Markdown")
    result = await client.switch_branch(branch=branch_name)

    if _is_unauthorized(result):
        await update.message.reply_text("❌ Session het han. Vui long chay `/start` de tao session moi.", parse_mode="Markdown")
        return
    if isinstance(result, dict) and "error" in result:
        msg = f"❌ Loi: {result['error']}"
    else:
        msg = f"✅ Phan hoi:\n```json\n{json.dumps(result, indent=2)}\n```"
    await update.message.reply_text(msg, parse_mode="Markdown")


async def cursor(update: Update, context: ContextTypes.DEFAULT_TYPE):
    client = await _require_client(update)
    if not client:
        return

    await update.message.reply_text("Dang lay trang thai Git...")
    result = await client.get_status()

    if _is_unauthorized(result):
        await update.message.reply_text("❌ Session het han. Vui long chay `/start` de tao session moi.", parse_mode="Markdown")
        return
    if isinstance(result, dict) and "error" in result:
        msg = f"❌ Loi: {result['error']}"
    else:
        msg = f"📍 Trang thai hien tai:\n```json\n{json.dumps(result, indent=2)}\n```"
    await update.message.reply_text(msg, parse_mode="Markdown")


async def fix(update: Update, context: ContextTypes.DEFAULT_TYPE):
    client = await _require_client(update)
    if not client:
        return
    if not context.args:
        await update.message.reply_text(
            "Cau lenh: `/fix <mo_ta_loi>`\nVi du: `/fix IndexError at line 10 in main.py`",
            parse_mode="Markdown",
        )
        return

    issue = " ".join(context.args)
    await update.message.reply_text(f"Dang gui yeu cau fix...\nTrace: `{issue}`", parse_mode="Markdown")
    result = await client.call_fix_api(trace_error=issue)

    if _is_unauthorized(result):
        await update.message.reply_text("❌ Session het han. Vui long chay `/start` de tao session moi.", parse_mode="Markdown")
        return
    if isinstance(result, dict) and "error" in result:
        msg = f"❌ Loi: {result.get('error')}"
    elif isinstance(result, dict) and "detail" in result and result.get("status_code") == 422:
        msg = f"❌ Validation Error: {result['detail']}"
    else:
        msg = f"✅ Da nhan yeu cau Fix:\n```json\n{json.dumps(result, indent=2)}\n```"
    await update.message.reply_text(msg, parse_mode="Markdown")


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    client = await _require_client(update)
    if not client:
        return
    if not context.args:
        await update.message.reply_text("Cau lenh: `/cancel <request_id>`", parse_mode="Markdown")
        return

    request_id = context.args[0]
    await update.message.reply_text(f"Dang huy task `{request_id}`...", parse_mode="Markdown")
    result = await client.call_cancel_fix(request_id=request_id)

    if _is_unauthorized(result):
        await update.message.reply_text("❌ Session het han. Vui long chay `/start` de tao session moi.", parse_mode="Markdown")
        return
    if isinstance(result, dict) and "error" in result:
        msg = f"❌ Loi: {result['error']}"
    else:
        msg = f"✅ Ket qua huy:\n```json\n{json.dumps(result, indent=2)}\n```"
    await update.message.reply_text(msg, parse_mode="Markdown")


async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    client = await _require_client(update)
    if not client:
        return

    await update.message.reply_text("Dang kiem tra status...")
    result = await client.get_status()

    if _is_unauthorized(result):
        await update.message.reply_text("❌ Session het han. Vui long chay `/start` de tao session moi.", parse_mode="Markdown")
        return
    if isinstance(result, dict) and "error" in result:
        msg = f"❌ Loi khi lay trang thai: {result['error']}"
    else:
        msg = f"📊 System Status:\n```json\n{json.dumps(result, indent=2)}\n```"
    await update.message.reply_text(msg, parse_mode="Markdown")


if __name__ == "__main__":
    asyncio.run(db.init())

    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("list", list_repo))
    app.add_handler(CommandHandler("repo", repo))
    app.add_handler(CommandHandler("branches", branches))
    app.add_handler(CommandHandler("cursor", cursor))
    app.add_handler(CommandHandler("fix", fix))
    app.add_handler(CommandHandler("cancel", cancel))
    app.add_handler(CommandHandler("status", status))

    print("Bot dang chay...")
    app.run_polling()
