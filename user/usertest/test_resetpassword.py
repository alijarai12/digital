# from django.contrib.auth import get_user_model
# from django.test import TestCase
# from django.urls import reverse
# from django.utils.http import urlsafe_base64_encode
# from django.utils.encoding import force_bytes
# from user.utils import account_activation_token
# from rest_framework import status


# class ResetPasswordTestCase(TestCase):
#     def setUp(self):
#         self.user = get_user_model().objects.create_user(
#             username="testuser",
#             password="testpassword",
#             email="test@example.com",
#         )

#     def test_reset_password_valid_link(self):
#         uidb64 = urlsafe_base64_encode(force_bytes(self.user.pk))
#         token = account_activation_token.make_token(self.user)
#         print(uidb64, token)

#         url = reverse("reset_password", args=[uidb64, token])
#         response = self.client.get(url)
#         # print(f'______________________________________________________')
#         # print(response.context)

#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         self.assertTemplateUsed(response, "forgot_password_confirm_password.html")
#         self.assertEqual(response.context["action"], "confirming")

#     def test_reset_password_invalid_link(self):
#         url = reverse("reset_password", args=["invalid_uidb64", "invalid_token"])
#         response = self.client.get(url)
#         # print(f'_________________________________________>>', response.context)

#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         self.assertTemplateUsed(response, "forgot_password_confirm_password.html")
#         self.assertEqual(response.context["action"], "invalid_link")

#     def test_reset_password_mismatched_passwords(self):
#         uidb64 = urlsafe_base64_encode(force_bytes(self.user.pk))
#         token = account_activation_token.make_token(self.user)

#         url = reverse("reset_password", args=[uidb64, token])
#         data = {"new_password": "newpassword1", "confirm_password": "newpassword2"}
#         response = self.client.post(url, data)
#         # print(f'______________________________________________________')
#         # print(response.context)

#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         self.assertTemplateUsed(response, "forgot_password_confirm_password.html")
#         self.assertEqual(response.context["action"], "mismatch")

#     def test_reset_password_successful(self):
#         uidb64 = urlsafe_base64_encode(force_bytes(self.user.pk))
#         token = account_activation_token.make_token(self.user)

#         url = reverse("reset_password", args=[uidb64, token])
#         data = {"new_password": "newpassword", "confirm_password": "newpassword"}
#         response = self.client.post(url, data)
#         # print(f'______________________________________________________')
#         # print(response.context)

#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         self.assertTemplateUsed(response, "forgot_password_confirm_password.html")
#         self.assertEqual(response.context["action"], "success")

#         # Verify that the password has been changed
#         self.user.refresh_from_db()
#         self.assertTrue(self.user.check_password("newpassword"))
