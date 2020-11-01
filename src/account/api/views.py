from account.api.serializers import ContactSerializer, UserSerializer
from account.filters import ContactFilterAPI, UserFilterAPI
from account.models import Contact, User

from django_filters import rest_framework as filters

from rest_framework.authentication import SessionAuthentication
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.permissions import IsAdminUser, IsAuthenticated

from rest_framework_simplejwt.authentication import JWTAuthentication


class UserListCreateView(ListCreateAPIView):
    permission_classes = [IsAdminUser]
    authentication_classes = [SessionAuthentication]

    queryset = User.objects.all()
    serializer_class = UserSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = UserFilterAPI


class UserReadUpdateDeleteView(RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAdminUser]
    authentication_classes = [SessionAuthentication]

    queryset = User.objects.all()
    serializer_class = UserSerializer


class ContactCreateView(ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    queryset = Contact.objects.all()
    serializer_class = ContactSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = ContactFilterAPI
