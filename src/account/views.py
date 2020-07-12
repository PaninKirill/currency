from account.forms import SignUpForm
from account.models import Contact, User
from account.serializers import UserSerializer
from account.tasks import send_email_async
from account.tokens import account_activation_token

from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.utils.encoding import force_text
from django.utils.http import urlsafe_base64_decode
from django.views.generic import CreateView, UpdateView

from mixins.mixins import AdminRequiredMixin

from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView


class ContactUs(CreateView):
    template_name = 'contact-us.html'
    model = Contact
    fields = ('email_from', 'title', 'message')
    success_url = reverse_lazy('index')

    def form_valid(self, form):
        result = super().form_valid(form)
        send_email_async.delay(form.cleaned_data)
        return result


class MyProfile(LoginRequiredMixin, UpdateView):
    template_name = 'user-edit.html'
    queryset = User.objects.all()
    fields = ('email', 'first_name', 'last_name', 'avatar')
    success_url = reverse_lazy('index')

    def get_object(self, queryset=None):
        obj = self.get_queryset().get(id=self.request.user.id)
        return obj


class SignUp(CreateView):
    template_name = 'user-sign-up.html'
    model = User
    success_url = reverse_lazy('index')
    form_class = SignUpForm


class Activate(UpdateView):
    queryset = User.objects.filter(is_active=False)

    def get_object(self, queryset=None):
        try:
            uidb64 = self.kwargs['uidb64']
            uid = force_text(urlsafe_base64_decode(uidb64))
            user = self.get_queryset().filter(pk=uid).last()
        except (TypeError, ValueError, OverflowError):
            user = None

        if user is None:
            raise Http404()

        return user

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        token = self.kwargs['token']

        if self.object is not None and account_activation_token.check_token(self.object, token):
            self.object.is_active = True
            self.object.save(update_fields=('is_active',))
            # login(request, self.object)
            return redirect('account:login')
        else:
            return render(request, 'account_activation_invalid.html')


class UserListCreateView(AdminRequiredMixin, ListCreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class UserReadUpdateDeleteView(AdminRequiredMixin, RetrieveUpdateDestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
