from account.models import Contact, User
from account.tasks import send_email_async

from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView


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
    fields = ('email', 'first_name', 'last_name')
    success_url = reverse_lazy('index')

    def get_object(self, queryset=None):
        obj = self.get_queryset().get(id=self.request.user.id)
        return obj
