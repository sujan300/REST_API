

# from django only ..
from django.contrib.auth import authenticate

# from rest-fromework only ....
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.http import Http404
from rest_framework.permissions import IsAuthenticated



#  from current api_account app only ...
from api_account.serializers import (UserRegisterSerializer,
        UserLogInSerializer,
        UserProfileSerializer,
        UserChangingPasswordSerializer,
        UserRestPasswordEmailSendSerializer,
        UserValidateAndResetPasswordSerializer
)
from api_account.models import AuthModel
from api_account.renderers import UserRenderer


# this is from rest_framework --> jwt 
from rest_framework_simplejwt.tokens import RefreshToken



# Create your views here.
# token generating function ...

def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)

    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }


class UserRegisterView(APIView):
    renderer_classes = [UserRenderer]
    # permission_classes = [IsAuthenticated]
    def get_user(self,pk):
        try:
            return AuthModel.objects.get(pk=pk)
        except(ValueError,AuthModel.DoesNotExist,TypeError,OverflowError):
            raise Http404
        
    def get(self,request,pk=None):
        if pk is not None:
            user=self.get_user(pk)
            serializer = UserRegisterSerializer(user)
            return Response({"data":serializer.data},status.HTTP_200_OK)
        else:
            users = AuthModel.objects.all()
            serializer = UserRegisterSerializer(users,many=True)
            return Response({"data":serializer.data},status.HTTP_200_OK)
        

    def post(self,request):
        serializer = UserRegisterSerializer(data=request.data)
        if serializer.is_valid():
            user=serializer.save()
            token = get_tokens_for_user(user)
            return Response({"token":token,"message":"register Successfully !","data":serializer.data},status.HTTP_201_CREATED)

        else:
            print(serializer.errors)
            return Response({"message":serializer.errors},status.HTTP_400_BAD_REQUEST)




class UserLogInView(APIView):
    renderer_classes = [UserRenderer]
    def post(self,request):
        serializer = UserLogInSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            email = serializer.data.get("email")
            password = serializer.data.get("password")
            user = authenticate(email=email,password=password)
            if user is not None:
                token = get_tokens_for_user(user)
                return Response({"token":token,"message":"Login Success"},status.HTTP_200_OK)
            else:
                return Response({"message":"email and password incorrect"},status.HTTP_404_NOT_FOUND)

        else:
            return Response({"message":"invalid data !"},status.HTTP_404_NOT_FOUND)


class UserProfileView(APIView):
    renderer_classes = [UserRenderer]
    permission_classes = [IsAuthenticated]
    def get(self,request):
        serializer = UserProfileSerializer(request.user)
        return Response({"data":serializer.data},status.HTTP_200_OK)

class UserPasswordChangeView(APIView):
    renderer_classes = [UserRenderer]
    permission_classes = [IsAuthenticated]
    def post(self,request):
        serializer = UserChangingPasswordSerializer(data=request.data,context={'user':request.user})
        if serializer.is_valid(raise_exception=True):
            return Response({"message":"your password has been changed successfully !"},status.HTTP_200_OK)
        else:
            return Response({"error":serializer.error},status.HTTP_400_BAD_REQUEST)            


class UserResetPasswordEmailSendView(APIView):
    renderer_classes = [UserRenderer]
    # permission_classes = [IsAuthenticated]

    def post(self,request):
        serializer = UserRestPasswordEmailSendSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            return Response({"message":"Please Check your email Box"},status.HTTP_200_OK)
        else:
            return Response({"error":serializer.error},status.HTTP_400_BAD_REQUEST)


class UserValidateAndResetPasswordView(APIView):
    renderer_classes = [UserRenderer]
    def post(self,request,uid,token):
        print("uid",uid)
        print("token",token)
        serializer = UserValidateAndResetPasswordSerializer(data=request.data,context={"uid":uid,"token":token})
        if serializer.is_valid(raise_exception=True):
            return Response({"message":"password changed SuccessFully !"},status.HTTP_200_OK)
        else:
            return Response(serializer.errors,status.HTTP_400_BAD_REQUEST)