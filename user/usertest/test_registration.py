# from django.test import TestCase
# from rest_framework.test import APIRequestFactory, APIClient
# from rest_framework import status
# from user.viewsets import UserViewset
# from user.models import UserProfile
# from django.contrib.auth.models import User


# class UserRegisterViewSetTest(TestCase):
#     def setUp(self):
#         self.client = APIClient()
#         self.factory = APIRequestFactory()

#     def test_create_valid_user(self):
#         url = "/api/v1/user/sign-up/"
#         data = {
#             "user_name": "Test",
#             "email": "test@example.com",
#             "username": "testuser",
#             "password": "testpassword",
#         }

#         request = self.factory.post(url)
#         response = self.client.post(url, data)
#         # print(response.data)
#         self.assertEqual(response.status_code, status.HTTP_201_CREATED)
#         expected_message = "User successfully registered. Please check your mail and verify your account"
#         self.assertEqual(response.data["message"], expected_message)

#     # email is not set to unique
#     # def test_create_existing_email(self):
#     #     existing_user = UserProfile.objects.create(user=User.objects.create_user(username="existinguser"), email="existing@example.com")
#     #     print(existing_user)

#     #     url = '/api/v1/user/sign-up/'
#     #     data = {
#     #         "first_name": "Test",
#     #         "email": "existing@example.com",
#     #         "username": "newuser",
#     #         "password": "newpassword"
#     #     }

#     #     request = self.factory.post(url)
#     #     response = self.client.post(url, data)
#     #     print(response.data)

#     #     self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

#     #     expected_message = "Email is already registered"
#     #     self.assertEqual(response.data["message"], expected_message)

#     def test_create_existing_username(self):
#         existing_user = UserProfile.objects.create(
#             user=User.objects.create_user(username="existinguser"),
#             email="existing@example.com",
#         )

#         data = {
#             "email": "new@example.com",
#             "username": "existinguser",
#             "password": "newpassword",
#         }

#         request = self.factory.post("/api/v1/user/sign-up/", data)

#         view = UserViewset.as_view({"post": "create"})

#         response = view(request)
#         # print(response.data)

#         self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

#         expected_message = "Username is already registered"
#         self.assertEqual(response.data["message"], expected_message)
