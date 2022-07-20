import base64
from os import access

import jwt
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.sites.shortcuts import get_current_site
from helpers.SendEmail import send_mail
from rest_framework import generics, permissions, status, viewsets
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from helpers.sendinblue import sendbluein

from .serializers import *

User = get_user_model()


class RegisterUserViewset(viewsets.ModelViewSet):
    """
    A viewset for creating users.
    """
    serializer_class = RegisterUserSerializer
    permission_classes = [permissions.AllowAny]
    http_method_names = ["post"]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(
            {
                "code": status.HTTP_201_CREATED,
                "status": "success",
                "message": "User created successfully",
            },
            status=status.HTTP_201_CREATED,
            headers=headers,
        )


class LoginUserViewset(viewsets.ModelViewSet):
    http_method_names = ["post"]

    serializer_class = LoginUserSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
    
        user = User.objects.get(email=serializer.data["email"])
        refresh_token = str(RefreshToken.for_user(user))
        access_token = str(RefreshToken.for_user(user).access_token)

        return Response(
            {
                "code": status.HTTP_200_OK,
                "status": "success",
                "message": "User logged in successfully",
                "access_token": access_token,
                "refresh_token": refresh_token,
            },
            status=status.HTTP_200_OK,
        )

class SendPasswordResetLinkViewSet(viewsets.ModelViewSet):

    http_method_names = ["post"]
    serializer_class = SendPasswordResetLinkSerializer

    def create(self, serializer):
        """
        This function sends a reset password link to the specified user email, if the user exists

        :param serializer: The serializer class that will be used to serialize the data
        :return: The response is a JSON object that contains a status and a message. The status is set to
        success if the email was sent successfully, and failed if the email was not sent successfully. The
        message is set to a success message if the email was sent successfully, and a failure message if the
        email was not sent successfully.
        """
        serializer = self.serializer_class(data=self.request.data)

        if serializer.is_valid(raise_exception=True):
            email = serializer.data["email"]

            try:
                self._send_activation_link(email)
            except User.DoesNotExist:
                return Response(
                    {
                        "code": status.HTTP_404_NOT_FOUND,
                        "status": "Failed",
                        "message": "User does not exist",
                    },
                    status=status.HTTP_404_NOT_FOUND,
                )
        return Response(
            {
                "code": status.HTTP_200_OK,
                "status": "success",
                "message": "Password reset link sent successfully",
            },
            status=status.HTTP_200_OK,
        )


    def _send_activation_link(self, email):
        user = User.objects.get(email=email)

        current_site = get_current_site(self.request).domain
        relative_url = "api/password-reset-confirm/"
        token = RefreshToken.for_user(user).access_token
        user_id = str(user.id).encode("ascii")
        user_id_encoded = base64.b64encode(user_id).decode("ascii")

        absolute_url = f"http://{current_site}/{relative_url}"

        context = {
            "password_reset_url": absolute_url,
            "first_name": user.first_name,
            "uid": user_id_encoded,
            "token": token,
        }

        send_mail(
            "Password Reset",
            "password_reset.html",
            "Auth App <noreply@gmail.com>",
            [user.email],
            context,
        )
        # sendbluein(
        #     "Password Reset",
        #     "ifexalex2@gmail.com",
        #     [user.email],
        # )





class PasswordResetConfirmViewSet(viewsets.ModelViewSet):
    serializer_class = ConfirmUserPasswordReset
    http_method_names = ["post"]

    def create(self, serializer):
        """
        This is the fuction that handles the password reset request. It takes in the token, uid, and
        password and checks if the token is valid. If it is, it checks if the user is active. If the
        user is active, it sets the password and saves the user.

        :param serializer: The serializer class that will be used to deserialize the request
        :return: The status code and the message.
        """
        serializer = self.serializer_class(data=self.request.data)

        if serializer.is_valid(raise_exception=True):
            token = serializer.validated_data["token"]
            uid = serializer.validated_data["uid"]
            password = serializer.validated_data["password"]

            current_site = get_current_site(self.request).domain
            absolute_url = f"http://{current_site}/api/login/"

            decoded_user_id = base64.b64decode(uid).decode("ascii")

            try:
                # The below code is decoding the token and validating it using the secret key.
                payload = jwt.decode(token, settings.SECRET_KEY, algorithms="HS512")
                try:

                    user = User.objects.get(id=decoded_user_id)
                except User.DoesNotExist:
                    return Response(
                        {
                            "code": status.HTTP_404_NOT_FOUND,
                            "status": "Failed",
                            "message": "invalid uid",
                        },
                        status=status.HTTP_404_NOT_FOUND,
                    )

                if user.is_active:
                    user.set_password(password)
                    user.save()
            except jwt.ExpiredSignatureError as identifer:
                return Response(
                    {
                        "code": status.HTTP_400_BAD_REQUEST,
                        "status": "Failed",
                        "message": "Token has expired",
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
            except jwt.exceptions.DecodeError as identifer:
                return Response(
                    {
                        "code": status.HTTP_400_BAD_REQUEST,
                        "status": "Failed",
                        "message": "Token is invalid",
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
            context = {
                "first_name": user.first_name,
                "absolute_url": absolute_url,
            }
            send_mail(
                "Password Reset Successful",
                "success_password_reset.html",
                "Auth App <noreply@gmail.com>",
                [user.email],
                context,
            )

        return Response(
            {
                "code": status.HTTP_200_OK,
                "status": "success",
                "message": "Password reset successful",
            },
            status=status.HTTP_202_ACCEPTED,
        )
