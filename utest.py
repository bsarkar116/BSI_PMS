import unittest
from pms import *
import requests


class TestPMS(unittest.TestCase):

    def test_checkpolicy(self):
        """
        Test that the complexity criteria of a generated password is evaluated as per current policy
        """
        result = checkpolicy('P@ssw0rd')
        self.assertEqual(result, False)

    def test_callhibp(self):
        """
        Test the invocation of HIBP API and check password leak status where 1 signifies a leak and 0 as safe
        """
        result1 = callhibp('P@ssw0rd')
        self.assertGreaterEqual(result1, 1)
        result2 = callhibp('Intel4770@3.4')
        self.assertEqual(result2, 0)

    def test_dbinsert(self):
        """
        Test whether insertion of data is persistent in the database by checking the rows returned
        """
        self.assertTrue(insertuser("abz@acme.com", "Intel4770@3.4A"))

    def test_passgenapi(self):
        """
        Test the invocation of password generation API for a single user by checking the response code returned
        """
        query = 'http://127.0.0.1:5000/passgen/anony@acme.com'
        result = requests.put(query)
        assert result.status_code == 200


if __name__ == '__main__':
    unittest.main()
