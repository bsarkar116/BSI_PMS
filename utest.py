import unittest
from pms import *
import requests


class TestPMS(unittest.TestCase):

    def test_checkpolicy(self):
        """
        Test that the complexity criteria of a generated password is evaluated as per current policy
        """
        result = check_policy('P@ssw0rd')
        self.assertEqual(result, False)

    def test_callhibp(self):
        """
        Test the invocation of HIBP API and check password leak status where 1 signifies a leak and 0 as safe
        """
        result1 = call_hibp('P@ssw0rd')
        self.assertGreaterEqual(result1, 1)
        result2 = call_hibp('Intel4770@3.4')
        self.assertEqual(result2, 0)

    def test_dbinsert(self):
        """
        Test whether insertion of data is persistent in the database by checking the boolean response of method
        """
        self.assertTrue(insert_user("abz@acme.com", "Intel4770@3.4A", "user", "a2"))

    def test_singlegenapi(self):
        """
        Test the invocation of password generation API for a single user by checking the response code returned
        """
        d = {"name": "anotst@acme.com", "role": "user"}
        query = 'http://127.0.0.1:5000/add/single'
        result = requests.post(query, d)
        assert result.status_code == 200

    def test_batchgenapi(self):
        """
        Test the invocation of password generation API for a batch of users by checking the response code returned
        """
        query = 'http://127.0.0.1:5000/add/multi'
        file = {'file': open("C:/Users/briji/OneDrive/Desktop/users_batch.csv", "rb")}
        result = requests.post(query, files=file)
        file.clear()
        assert result.status_code == 200


if __name__ == '__main__':
    unittest.main()
