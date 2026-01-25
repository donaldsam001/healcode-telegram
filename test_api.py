import unittest
from unittest.mock import patch, MagicMock
import healcode_api

class TestHealcodeApi(unittest.TestCase):

    def setUp(self):
        # Đảm bảo base URL giống trong code thực
        self.base_url = "http://localhost:8080"

    @patch('healcode_api.requests.post')
    def test_call_start_api_success(self, mock_post):
        # Giả lập phản hồi từ server
        mock_response = MagicMock()
        mock_response.json.return_value = {"status": "success", "user_id": 123}
        mock_response.status_code = 200
        mock_post.return_value = mock_response

        # Gọi hàm
        result = healcode_api.call_start_api("12345", "user_test", "token_abc")

        # Kiểm tra 1: Hàm post được gọi đúng URL chưa? (Check lỗi thiếu f-string)
        expected_url = f"{self.base_url}/start"
        mock_post.assert_called_once()
        args, kwargs = mock_post.call_args
        self.assertEqual(args[0], expected_url)
        
        # Kiểm tra 2: Payload gửi đi có đúng không?
        expected_json = {
            "id": "12345",
            "name": "user_test",
            "token": "token_abc"
        }
        self.assertEqual(kwargs['json'], expected_json)
        self.assertEqual(result, {"status": "success", "user_id": 123})

    @patch('healcode_api.requests.post')
    def test_call_repo_api(self, mock_post):
        mock_response = MagicMock()
        mock_response.json.return_value = {"status": "success"}
        mock_post.return_value = mock_response

        healcode_api.call_repo_api("http://git.com/repo", "main")

        # Kiểm tra URL endpoint
        mock_post.assert_called_with(
            f"{self.base_url}/repo",
            json={"url": "http://git.com/repo", "branch": "main"},
            timeout=30
        )

    @patch('healcode_api.requests.post')
    def test_call_fix_api(self, mock_post):
        # Test endpoint /api/fix/{repo_name}
        repo_name = "my-project"
        issue = "IndexError"
        
        mock_response = MagicMock()
        mock_response.json.return_value = {"request_id": "req_001"}
        mock_post.return_value = mock_response

        healcode_api.call_fix_api(repo_name, issue)

        # Kiểm tra URL dynamic
        expected_url = f"{self.base_url}/api/fix/{repo_name}"
        args, kwargs = mock_post.call_args
        self.assertEqual(args[0], expected_url)
        self.assertEqual(kwargs['json']['trace_error'], issue)

    @patch('healcode_api.requests.delete')
    def test_call_cancel_api(self, mock_delete):
        # Test method DELETE
        repo_name = "my-project"
        request_id = "req_999"
        
        mock_response = MagicMock()
        mock_response.json.return_value = {"message": "Cancelled"}
        mock_delete.return_value = mock_response

        healcode_api.call_cancel_api(repo_name, request_id)

        expected_url = f"{self.base_url}/api/fix/{repo_name}/cancel/{request_id}"
        mock_delete.assert_called_once()
        self.assertEqual(mock_delete.call_args[0][0], expected_url)

if __name__ == '__main__':
    unittest.main()