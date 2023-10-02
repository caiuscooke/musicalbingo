from django.shortcuts import render, redirect
from django.core.mail import send_mail
import logging

# Create your views here.


def home(request):
    logger = logging.getLogger(__name__)
    try:
        return render(request, 'portfolio/home.html')
    except Exception as e:
        logger.error(f"Failed with error of {str(e)}")
        return render(request, 'portfolio/home.html')


def about_me(request):
    return render(request, 'portfolio/aboutme.html')


def works(request):
    return render(request, 'portfolio/works.html')


def contact_form(request):
    if request.method == 'POST':
        name = request.POST.get('name', '')
        email = request.POST.get('email', '')
        message = request.POST.get('message', '')

        # Your email sending code here
        recipient_list = ['cookecaius@gmail.com']
        subject = f"New Contact Request From {name}"
        send_mail(subject=subject, from_email=email,
                  message=message, recipient_list=recipient_list)

        # Redirect to the 'home' page or your desired destination
        return redirect('home')
