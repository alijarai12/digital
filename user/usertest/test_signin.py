# from django.test import TestCase
# from django.urls import reverse
# from rest_framework import status
# from rest_framework.test import APIClient
# from django.contrib.auth.models import User


# class UserSignInTest(TestCase):
#     def setUp(self):
#         self.client = APIClient()
#         self.url = "/api/v1/user/sign-in/"

#         # Create a test user
#         self.user = User.objects.create_user(
#             username="testuser", email="test@example.com", password="testpassword"
#         )

#     def test_user_signin_success(self):
#         data = {
#             "username": "testuser",
#             "password": "testpassword",
#         }

#         response = self.client.post(self.url, data)
#         # print(response.data)

#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         self.assertIn("token", response.data)
#         self.assertIn("user_id", response.data)
#         self.assertIn("email", response.data)
#         self.assertIn("username", response.data)

#     def test_user_signin_invalid_password(self):
#         data = {
#             "username": "testuser",
#             "password": "invalidpassword",
#         }

#         response = self.client.post(self.url, data)
#         # print(response.data)

#         self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
#         self.assertEqual(response.data["message"], "Invalid password")

#     def test_user_signin_user_not_found(self):
#         data = {
#             "username": "nonexistentuser",
#             "password": "testpassword",
#         }

#         response = self.client.post(self.url, data)
#         # print(response.data)

#         self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
#         self.assertEqual(response.data["message"], "User does not exist.")
