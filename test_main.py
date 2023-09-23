import main
import unittest
import sqlite3
from unittest import mock

db_path = './app_data/dbase.db'

class userTests(unittest.TestCase):

    test_telegram_id = 99999999999999
    test_telegram_id_for_creation = 999999999999991

    def setUp(self):
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute('CREATE TABLE IF NOT EXISTS users (telegram_id INTEGER PRIMARY KEY)')
        cursor.execute('INSERT INTO users (telegram_id) VALUES (?)', (self.test_telegram_id,))
        conn.commit()
        conn.close()
    
    def testCheckUserExistance(self):
        user = main.User(self.test_telegram_id)
        result = user.checkUserRecord()
        self.assertEqual(result,self.test_telegram_id)

    def testCreateUser(self):
        user = main.User(self.test_telegram_id_for_creation)
        user.createUserRecord()
        result_check = user.checkUserRecord()
        self.assertEqual(result_check, self.test_telegram_id_for_creation)
    
    def tearDown(self):
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute('DELETE FROM users WHERE telegram_id = ?', (self.test_telegram_id,))
        cursor.execute('DELETE FROM users WHERE telegram_id = ?', (self.test_telegram_id_for_creation,))
        conn.commit()
        conn.close()

class srockTests(unittest.TestCase):

    def testCheckStockEsixtance(self):
        
        test_stock_id  = "SBER"
        test_response_json = {"boards":{"data": [["SBER"]]}}
        
        with mock.patch('requests.get') as mock_get:

            mock_response_success = mock.Mock()
            mock_response_success.status_code = 200
            mock_response_success.json.return_value = test_response_json

            mock_response_error = mock.Mock()
            mock_response_error.status_code = 400
            mock_response_error.json.return_value = None

            mock_get.return_value = mock_response_success
            result_success = main.checkStockExistance(test_stock_id)
            self.assertTrue(result_success)

            mock_get.return_value = mock_response_error
            result_error = main.checkStockExistance(test_stock_id)
            self.assertFalse(result_error)

    def testGetStockPrice(self):
        
        test_stock_id  = "SBER"
        test_response_json = {"securities":{"data": [[100.0, "SUR"]]}}
        
        with mock.patch('requests.get') as mock_get:

            mock_response_success = mock.Mock()
            mock_response_success.status_code = 200
            mock_response_success.json.return_value = test_response_json

            mock_response_error = mock.Mock()
            mock_response_error.status_code = 400
            mock_response_error.json.return_value = None

            mock_get.return_value = mock_response_success
            result_success = main.getStockPrice(test_stock_id)
            self.assertEqual(result_success, "100.0 RUB")

            mock_get.return_value = mock_response_error
            result_error = main.getStockPrice(test_stock_id)
            self.assertFalse(result_error)

if __name__ == '__main__':
    unittest.main()



