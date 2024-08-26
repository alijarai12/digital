# from django.contrib.auth.models import User
# from rest_framework.test import APITestCase
# from rest_framework import status


# class ChangePasswordTestCase(APITestCase):
#     def setUp(self):
#         self.user = User.objects.create_user(
#             username="testuser", password="testpassword"
#         )
#         self.client.login(username="testuser", password="testpassword")

#     def test_change_password(self):
#         url = "/api/v1/user/change-password/"

#         data = {
#             "old_password": "testpassword",
#             "new_password": "newpassword",
#             "confirm_password": "newpassword",
#         }
#         response = self.client.post(url, data, format="json")
#         # print(response.data)

#         self.assertEqual(response.status_code, status.HTTP_201_CREATED)
#         self.assertEqual(response.data, {"Message": "Password Successfuly Updated."})

#         # Verify that the password has been changed
#         self.user.refresh_from_db()
#         self.assertTrue(self.user.check_password("newpassword"))

#     def test_change_password_with_incorrect_old_password(self):
#         url = "/api/v1/user/change-password/"

#         data = {
#             "old_password": "wrongpassword",
#             "new_password": "newpassword",
#             "confirm_password": "newpassword",
#         }
#         response = self.client.post(url, data, format="json")
#         # print(response.data)

#         self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
#         self.assertEqual(response.data, {"Error": "Incorrect old password"})

#     def test_change_password_with_mismatched_new_passwords(self):
#         url = "/api/v1/user/change-password/"

#         data = {
#             "old_password": "testpassword",
#             "new_password": "newpassword1",
#             "confirm_password": "newpassword2",
#         }
#         response = self.client.post(url, data, format="json")
#         # print(response.data)

#         self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
#         self.assertEqual(
#             response.data, {"Error": "New and Confirm passwords do not match."}
#         )
