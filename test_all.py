import unittest
from posting_system_final import generate_post, setup_twitter_api

class TestPostingSystem(unittest.TestCase):
    def test_generate_post(self):
        post = generate_post()
        self.assertIsInstance(post, str)
        self.assertTrue(len(post) > 0)
    
    def test_twitter_api_setup(self):
        api = setup_twitter_api()
        self.assertIsNotNone(api)

if __name__ == '__main__':
    unittest.main()
