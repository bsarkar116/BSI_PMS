import unittest
from pms import *
from policy import *
from tokens import *
from schema import *
from validations import *
import requests
from datetime import datetime


class Create:
    def __init__(self, user, role, appid):
        self.dic = {'Length': 10, 'Upper': 2, 'Lower': 2, 'Digits': 2, 'Special': 2, 'Age': 40,
                    'Date': datetime.today().strftime(time_format)}
        self.user = user
        self.role = role
        self.appid = appid
        self.json_user = {"user": "test"}
        self.json_policy = {'Length': 10, 'Upper': 2, 'Lower': 2, 'Digits': 2, 'Special': 2, 'Age': 40}
        self.json_login = {"user": "brij@acme.com", "pass": "asachbee"}
        self.json_remove = {"user": "brij@acme.com"}
        self.jtext = None
        self.url = "https://localhost:5000/"
        self.df1 = pd.read_csv("test_users_batch.csv")
        self.df2 = pd.read_csv("test_users_remove.csv")

    def create_user(self):
        insert_user(self.user, "Intel4770@3.4", self.role, self.appid)

    def delete_user(self):
        del_user(self.user)


class TestPMS(unittest.TestCase):
    def test_db_funcs(self):
        """
        Test insert, select, update and delete operations of data in the database
        """
        # Insert function
        self.assertTrue(insert_user("abz1@acme.com", "Intel4770@3.4A", "user", "a2"))
        # Select function
        rows = lookup_user("abz1@acme.com")
        self.assertIsNotNone(rows)
        # Update password function
        updatep("abz1@acme.com", "Intel4770@3.4B")
        rows = lookup_user("abz1@acme.com")
        if rows:
            self.assertEqual(rows[0][1], "Intel4770@3.4B")
        # Delete user function
        self.assertTrue(del_user("abz1@acme.com"))

    def test_call_hibp(self):
        """
        Test the invocation of HIBP API and check password leak status where 1 signifies a leak and 0 as safe
        """
        response1 = call_hibp('P@ssw0rd')
        self.assertGreaterEqual(response1, 1)
        response2 = call_hibp('Intel4770@3.4')
        self.assertEqual(response2, 0)

    def setUp(self) -> None:
        self.create = Create("abz2@acme.com", "admin", "a2")
        self.create1 = Create("abz2@acme.com", "admin", "a2")
        self.create1.create_user()

    def tearDown(self) -> None:
        self.create.delete_user()
        self.create1.delete_user()
        del self.create

    def test_policy(self):
        """
        Test the logic of password policy, creation of policy file and retention policy
        """
        # Generate policy
        gen_policy(10, 2, 2, 2, 2, 40)
        self.assertEqual(load_policy(), self.create.dic)
        # Check password against current policy
        response = check_policy('P@ssw0rd')
        self.assertFalse(response)
        # Verify password retention policy
        self.assertTrue(pass_retention())

    def test_pass_gen(self):
        """
        Test random password generation for a user and compare hashed password from database
        """
        response, passw = adduser(self.create.user, self.create.role, self.create.appid)
        if response:
            self.assertTrue(compare_hash(self.create.user, passw))

    def test_token_creation(self):
        """
        Test token creation and verification
        """
        token = create_token(self.create1.user)
        self.assertIsNotNone(verify_token(token))

    def test_json_validations(self):
        """
        Test the json input validations for API calls
        """
        # JSON Schema for password policy
        self.assertTrue(validate_json(self.create.json_policy, policySchema))
        # JSON Schema for user information
        self.assertFalse(validate_json(self.create.json_user, userSchema))
        # JSON Schema for user login
        self.assertTrue(validate_json(self.create.json_login, loginSchema))
        # JSON Schema for user removal
        self.assertTrue(validate_json(self.create.json_remove, removeSchema))

    def test_csv_validations(self):
        """
        Test validation of CSV batch file for API calls
        """
        # CSV for batch of users to be added
        self.assertTrue(validate_csv(self.create.df1))
        # CSV for batch of users to be removed
        self.assertTrue(validate_csv(self.create.df2))

    def test_user_auth(self):
        """
        Test user authentication API call
        """
        query = self.create.url
        d = {"user": self.create.user, "pass": "H8kWtE`5!`"}
        response = requests.get(query + "auth", json=d, verify='cert.pem')
        self.assertIsNotNone(response)

    def test_add_user_api(self):
        """
        Test user creation API call
        """
        query = self.create.url
        # Single user creation
        header1 = {'auth-tokens': "dummy token"}
        d = {"user": "arcon@acme.com", "role": "user", "appid": "a1"}
        response = requests.post(query + "add/single", json=d, headers=header1, verify='cert.pem')
        self.assertIsNotNone(response)
        # Batch user creation
        flag = 1
        file = {'file': open("test_users_batch.csv", "rb")}
        header2 = {'auth-tokens': "dummy token"}
        response = requests.post(query + "add/multi", files=file, headers=header2, verify='cert.pem')
        self.assertIsNotNone(response)

    def test_remove_user_api(self):
        """
        Test user removal API call
        """
        query = self.create.url
        # Single user creation
        header1 = {'auth-tokens': "dummy token"}
        d = {"user": "arcon@acme.com", "role": "user", "appid": "a1"}
        response = requests.post(query + "del/single", json=d, headers=header1, verify='cert.pem')
        self.assertIsNotNone(response)
        # Batch user creation
        flag = 1
        file = {'file': open("test_users_remove.csv", "rb")}
        header2 = {'auth-tokens': "dummy token"}
        response = requests.post(query + "del/multi", files=file, headers=header2, verify='cert.pem')
        self.assertIsNotNone(response)


if __name__ == '__main__':
    unittest.main()
