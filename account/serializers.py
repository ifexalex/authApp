from django.forms import PasswordInput
from rest_framework import serializers
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
import re

# Getting the user model from the settings.py file.
User = get_user_model()


class RegisterUserSerializer(serializers.ModelSerializer):


    # confirm_password = serializers.CharField(
    #     style={"input_type": "password"},
    #     required=True, 
    #     help_text="Password",
    # )

    class Meta:
        model = User
        fields = [
            "email",
            "first_name",
            "last_name",
            "phone_number",
            "address",
            "city",
            "country",
            "password",
            "confirm_password",
        ]
        extra_kwargs = {
            "password": {"write_only": True},
            "confirm_password": {"write_only": False},
        }

    def create(self, validated_data):
        if validated_data.get("phone_number", None) is not None:
            validated_data["phone_number"] = validated_data["phone_number"].replace(
                "-", ""
            )
        return User.objects.create_user(**validated_data)

    def validate(self, data):
        strong_password = re.compile("[^0-9a-zA-Z]+")
        password_string = str(data.get("password", None))

        print(data["confirm_password"])


        if data["password"] != data["confirm_password"]:
            raise serializers.ValidationError("Passwords do not match")
        if strong_password.search(password_string) is None:
            raise serializers.ValidationError(
                {
                    "password": "password must contain at least one special character e.g @#$%"
                }
            )
        return data



class LoginUserSerializer(serializers.Serializer):
    # def validate(self, attrs):
    #     data = super().validate(attrs)
    #     data["user"] = User.objects.get(email=data["email"])
    #     return data

    email = serializers.EmailField(required=True)
    password = serializers.CharField(
        style={"input_type": "password"},
        required=True,
        help_text="Password",
    )

    class Meta:
        fields = ("email", "password")

    def validate(self, data):
        user_obj = User.objects.filter(email=data["email"]).first()
        if user_obj is None:
            raise serializers.ValidationError("User with the given email does not exist")
        if not user_obj.check_password(data["password"]):
            raise serializers.ValidationError("Invalid email or password")
        return data


class ResetPasswordSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        style={"input_type": "password"},
        write_only=True,
        required=True,
        help_text="Password",
    )
    confirm_password = serializers.CharField(
        style={"input_type": "password"},
        required=True, 
        help_text="Password",
    )

    class Meta:
        model = User
        fields = [
            "password",
            "confirm_password",
        ]

    def validate(self, data):
        strong_password = re.compile("[^0-9a-zA-Z]+")
        password_string = str(data.get("password", None))


        if data["password"] != data["confirm_password"]:
            raise serializers.ValidationError("Passwords do not match")
        if strong_password.search(password_string) is None:
            raise serializers.ValidationError(
                {
                    "password": "password must contain at least one special character e.g @#$%"
                }
            )
        return data

    def update(self, instance, validated_data):
        instance.set_password(validated_data["password"])
        instance.save()
        return instance



class SendPasswordResetLinkSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=True)

    class Meta:
        model = User
        fields = ["email"]


class ConfirmUserPasswordReset(serializers.ModelSerializer):
    uid = serializers.CharField(required=True)
    token = serializers.CharField(required=True)

    password = serializers.CharField(
        style={"input_type": "password"},
        required=True,
        help_text="Password",
    )
    confirm_password = serializers.CharField(
        style={"input_type": "password"},
        required=True,
        help_text="confirm Password",
    )

    class Meta:
        model = User
        fields = ["uid", "token", "password", "confirm_password"]

    def validate(self, data):
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError("Passwords do not match")
        return data