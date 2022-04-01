from rest_framework.serializers import ModelSerializer
from .models import AuthModel
from rest_framework import serializers


#  for links 
from django.utils.encoding import DjangoUnicodeDecodeError,smart_bytes,force_bytes
from django.utils.http import urlsafe_base64_decode,urlsafe_base64_encode
from django.contrib.auth.tokens import PasswordResetTokenGenerator


class UserRegisterSerializer(ModelSerializer):
    password2 = serializers.CharField(style={'input_type':'password'},write_only=True)
    class Meta:
        model = AuthModel
        fields = ["id","name","email","phone","password","password2"]
        extra_kwargs = {
            "password":{'write_only':True}
        }
    def validate(self, attrs):
        password = attrs.get("password")
        password2 = attrs.get("password2")
        if password !=password2:   
            raise serializers.ValidationError("password Doesn't match with confirm password")
        return attrs


    def create(self,validate_data):
        validate_data.pop('password2', None)
        return AuthModel.objects.create_user(**validate_data)


class UserLogInSerializer(ModelSerializer):
    email = serializers.EmailField(max_length=50)
    class Meta:
        model = AuthModel
        fields = ['email','password']


class UserProfileSerializer(ModelSerializer):
    class Meta:
        model = AuthModel
        fields = ["id","name","email"]


class UserChangingPasswordSerializer(serializers.Serializer):
    password = serializers.CharField(style={'input_type':'password'},write_only=True)
    password2 = serializers.CharField(style={'input_type':'password'},write_only=True)
    class Meta:
        fields = ['password','password2']
    def validate(self,attrs):
        password = attrs.get('password')
        password2 = attrs.get('password2')
        user = self.context.get("user")
        if password != password2:
            raise serializers.ValidationError("password doesn't match !")
        user.set_password(password)
        user.save()
        return attrs

class UserRestPasswordEmailSendSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=50)
    class Meta:
        fields = ["email"]
    def validate(self,attrs):
        email = attrs.get("email")
        print("email is ==>",email)
        if AuthModel.objects.filter(email=email).exists():
            user = AuthModel.objects.get(email=email)
            uid = urlsafe_base64_encode(force_bytes(user.id))
            token = PasswordResetTokenGenerator().make_token(user)
            url = f"http://localhost:7500/api/user/validate-link/{uid}/{token}"
            # send email  to user
        else:
            raise serializers.ValidationError("Not Register User Register first !")
        return attrs


class UserValidateAndResetPasswordSerializer(serializers.Serializer):
    password = serializers.CharField(style={'input_type':'password'})
    password2= serializers.CharField(style={'input_type':'password'})
    class Meta:
        fields = ["password","password2"]
    def validate(self,attrs):
        try:
            password = attrs.get('password')
            password2 = attrs.get('password2')
            uid = self.context.get("uid")
            token = self.context.get("token")
            if password != password2:
                raise serializers.ValidationError("password doesn't match !")

            id = smart_bytes(urlsafe_base64_decode(uid))
            user = AuthModel.objects.get(pk=id)
            if not PasswordResetTokenGenerator().check_token(user, token):
                raise serializers.ValidationError("link expired or not valid")
            user.set_password(password)
            user.save()
            return attrs
        except DjangoUnicodeDecodeError:
            PasswordResetTokenGenerator().check_token(user, token)
            raise serializers.ValidationError("link expired or not valid")