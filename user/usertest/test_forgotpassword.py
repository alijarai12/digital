# from django.contrib.auth.models import User
# from rest_framework.test import APITestCase
# from rest_framework.authtoken.models import Token
# from django.urls import reverse
# from rest_framework import status


# class ForgotPasswordTestCase(APITestCase):
#     def setUp(self):
#         self.user = User.objects.create_user(
#             username="testuser", password="testpassword", email="test@example.com"
#         )
#         self.token = Token.objects.create(user=self.user)

#     def test_forgot_password_existing_user(self):
#         self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.token}")

#         url = reverse("forgot_password")
#         data = {"email": "test@example.com"}
#         response = self.client.post(url, data, format="json")
#         # print(response.data)

#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         self.assertEqual(
#             response.data,
#             {
#                 "Message": "We have sent an link to reset your password. Please check your email"
#             },
#         )

#     def test_forgot_password_nonexistent_user(self):
#         self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.token}")

#         url = reverse("forgot_password")
#         data = {"email": "nonexistent@example.com"}
#         response = self.client.post(url, data, format="json")
#         # print(response.data)

#         self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
#         self.assertEqual(
#             response.data, {"Message": "User does not exists with this email."}
#         )
