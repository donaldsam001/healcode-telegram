import unittest
from unittest.mock import AsyncMock, patch, MagicMock
import bot
from telegram import Update, User, Message, Chat
from telegram.ext import ContextTypes

class TestBotHandlers(unittest.IsolatedAsyncioTestCase):

    async def asyncSetUp(self):
        # Tạo Mock cho Update và Context
        self.update = MagicMock(spec=Update)
        self.context = MagicMock(spec=ContextTypes.DEFAULT_TYPE)
        
        # Mock User
        self.user = User(id=123456, first_name="TestUser", is_bot=False)
        self.update.effective_user = self.user
        
        # Mock Message để check hàm reply_text
        self.message = AsyncMock(spec=Message)
        self.update.message = self.message

    @patch('bot.call_start_api') 
    async def test_start_command_success(self, mock_api):
        # Setup: Giả lập user nhập đúng token
        self.context.args = ["ghp_token123"]
        
        # Setup: Giả lập API trả về thành công
        mock_api.return_value = {"status": "connected"}

        # Chạy hàm handler
        await bot.start(self.update, self.context)

        # Kiểm tra:
        # 1. API phải được gọi với đúng ID và Token
        mock_api.assert_called_with("123456", "TestUser", "ghp_token123")
        
        # 2. Bot phải reply lại text chứa nội dung API trả về
        self.message.reply_text.assert_called()
        # Lấy nội dung tin nhắn bot đã gửi
        args, _ = self.message.reply_text.call_args
        sent_text = args[0]
        self.assertIn("TestUser", sent_text)
        self.assertIn("connected", sent_text)

    async def test_start_command_missing_token(self):
        # Setup: User không nhập token (args rỗng)
        self.context.args = []

        await bot.start(self.update, self.context)

        # Kiểm tra: Bot phải báo lỗi
        args, _ = self.message.reply_text.call_args
        self.assertIn("Vui lòng nhập token", args[0])

    @patch('bot.call_repo_api')
    async def test_repo_command(self, mock_api):
        # Setup: User nhập đúng 2 tham số
        self.context.args = ["https://github.com/a/b", "main"]
        
        mock_api.return_value = {
            "status": "success", 
            "message": "Cloned", 
            "local_path": "/tmp/a"
        }

        await bot.repo(self.update, self.context)

        # Kiểm tra gọi API
        mock_api.assert_called_with("https://github.com/a/b", "main")
        
        # Kiểm tra phản hồi thành công
        args, _ = self.message.reply_text.call_args
        self.assertIn("✅ **Thành công:**", args[0])

    @patch('bot.call_fix_api')
    async def test_fix_command_logic(self, mock_api):
        # Case 1: Thiếu tham số
        self.context.args = ["only_repo_name"] 
        await bot.fix(self.update, self.context)
        # Kiểm tra cảnh báo cú pháp (gọi lần 1)
        self.assertIn("Cú pháp: /fix", self.message.reply_text.call_args_list[0][0][0])

        # Reset mock để test case 2
        self.message.reply_text.reset_mock()
        
        # Case 2: Đủ tham số
        self.context.args = ["my-repo", "Lỗi", "dòng", "10"] # User nhập: /fix my-repo Lỗi dòng 10
        mock_api.return_value = {"request_id": "req_123", "status": "pending", "message": "queued"}
        
        await bot.fix(self.update, self.context)
        
        # Kiểm tra API ghép chuỗi lỗi đúng không ("Lỗi dòng 10")
        mock_api.assert_called_with("my-repo", "Lỗi dòng 10")
        
        # Kiểm tra bot báo thành công
        args, _ = self.message.reply_text.call_args
        self.assertIn("req_123", args[0])

if __name__ == '__main__':
    unittest.main()