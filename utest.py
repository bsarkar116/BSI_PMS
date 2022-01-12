import unittest
from pms import *
import requests


class TestPMS(unittest.TestCase):

    def test_checkpolicy(self):
        """
        Test that the complexity of password generated is evaluated as per current policy
        """
        result = checkpolicy('P@ssw0rd')
        self.assertEqual(result, 0)

    def test_callhibp(self):
        """
        Test the invocation of HIBP API and check password leak status
        """
        result1 = callhibp('P@ssw0rd')
        self.assertGreaterEqual(result1, 1)
        result2 = callhibp('Intel4770@3.4')
        self.assertEqual(result2, 0)

    def test_dbinsert(self):
        """
        Test whether insertion of data is persistent in database by checking the rows returned
        """
        insertuser("abx@acme.com", "Intel4770@3.4A")
        self.assertTrue(lookup("abx@acme.com"))

    def test_passgenapi(self):
        """
        Test the invocation of password generation API for a single user by checking the response code returned
        """
        query = 'http://127.0.0.1:5000/passgen/anon@acme.com'
        result = requests.put(query)
        assert result.status_code == 200


if __name__ == '__main__':
    unittest.main()
