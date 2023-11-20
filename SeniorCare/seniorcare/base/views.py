from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login,logout
from django. contrib import messages
from .models import senior_list
from .forms import register_form
from django.db.models import Q
from django.shortcuts import redirect, get_object_or_404
from django.utils import timezone
from django.urls import reverse
from django.http import HttpResponse
import csv

from django.conf import settings
from django.http import JsonResponse
from twilio.rest import Client

import json
import base64
import numpy as np
import cv2
import os
from datetime import datetime
from django.views.decorators.csrf import csrf_exempt
import face_recognition
import dlib



# Create your views here.

def index(request):
    return render(request, 'index.html'  )

def index(request):
    page='index'
    if request.method =='POST':
        username= request.POST.get('username')
        password = request.POST.get('password')

        try:
            user = User.objects.get(username=username)
        except: 
            messages.error(request, 'User does not exist') #if the user does not exist

        user=authenticate(request, username=username, password=password) #to make sure the credentials are correct

        if user is not None:
            login(request, user)
            return redirect(home_page)
        else:
            messages.error(request, 'Invalid Username and Password') #if the user does not exist
    context ={'page':page}
    return render(request, 'index.html', context)

def home_page(request):
    return render(request, 'home_page.html'  )

def register_page(request):
    return render(request, 'register_page.html')

def main_page(request):
    return render(request, 'main.html')

def register_page(request):
    form = register_form()
    if request.method == 'POST':
        form = register_form(request.POST, request.FILES)  
        if form.is_valid():
            seniors = form.save()
            return redirect('preview', id=seniors.id)

    context = {'form': form}
    return render(request, 'register_page.html', context)

def update_page(request):
    seniors = senior_list.objects.all()
    return render(request, 'update_page.html', {'seniors': seniors})

def update_viewinfo_page(request, id):
    seniors = senior_list.objects.get(id=id)
    return render(request, 'update_viewinfo_page.html', {'seniors': seniors})

def edit(request, id):
    seniors = senior_list.objects.get(id=id)
    return render(request, 'edit.html', {'seniors': seniors})




#pahirap to pero working na siya ngayon
def update(request, id):
    firstname = request.POST['Firstname']
    lastname = request.POST['Lastname']
    middlename = request.POST['Middlename']
    suffix = request.POST['Suffix']
    sex = request.POST['sex']
    #birthdate = request.POST['Birthdate']
    age = request.POST['Age']
    address = request.POST['Adress']
    if request.method == 'POST':
        seniors = senior_list.objects.get(id=id)
        seniors.first_name = firstname
        seniors.last_name = lastname
        seniors.middle_name = middlename
        seniors.suffix = suffix
        seniors.sex = sex
    #seniors.birth_date = birthdate cinomment ko to kasi di tinatanggap ng model ung format ng date na nakadisplay sa viewinfo page kaya dinisable ko para di mag-error
        seniors.age = age
        seniors.address = address
        seniors.save()
        return redirect(update_page)
        
    seniors = senior_list.objects.all()
    return redirect('update_viewinfo_page', seniors.id,  {'seniors': seniors})
    

#oks na to delete function
def delete(request, id):
    seniors = senior_list.objects.get(id=id)
    seniors.delete()
    return redirect(update_page)


def search(request):
    if 'q' in request.GET:
        q= request.GET['q']
        #seniors= senior_list.objects.filter(last_name__icontains=q)
        multiple_q=Q(Q(last_name__icontains=q) | Q(first_name__icontains=q))
        seniors = senior_list.objects.filter(multiple_q)
    else:
        seniors=senior_list.objects.all()
    context={'seniors': seniors}
    return render(request, 'update_page.html', context)

def search1(request):
    if 'q' in request.GET:
        q= request.GET['q']
        #seniors= senior_list.objects.filter(last_name__icontains=q)
        multiple_q=Q(Q(last_name__icontains=q) | Q(first_name__icontains=q))
        seniors = senior_list.objects.filter(multiple_q)
    else:
        seniors=senior_list.objects.all()
    context={'seniors': seniors}
    return render(request, 'claim_page.html', context)

def claim_page(request):
    seniors = senior_list.objects.all()
    return render(request, 'claim_page.html', {'seniors': seniors})

def claim_detail_page(request, id):
    seniors = senior_list.objects.get(id=id)
    return render(request, 'claim_detail_page.html', {'seniors': seniors})

def claimed_success(request, id):
    seniors = senior_list.objects.get(id=id)
    return render(request, 'claimed_success.html', {'seniors': seniors})


def claimed_succesfully(request, id):
    seniors = get_object_or_404(senior_list, pk=id)
    seniors.is_claimed = True
    seniors.claimed_date = timezone.now()
    seniors.save()

    context = {
        'last_name': seniors.last_name,
        'first_name': seniors.first_name,
        'middle_name': seniors.middle_name,
        'OSCA_ID': seniors.OSCA_ID,
        'claimed_date': seniors.claimed_date,
    }
    return render(request, 'claimed_success.html', context)


def claim_verify_page(request):
    claimed_seniors = senior_list.objects.filter(is_claimed=True).order_by('last_name')
    unclaimed_seniors = senior_list.objects.filter(is_claimed=False).order_by('last_name')
    seniors = list(claimed_seniors) + list(unclaimed_seniors)

    return render(request, 'claim_verify_page.html', {'seniors': seniors})

def claim_summary_page(request):
    claimed_seniors = senior_list.objects.filter(is_claimed=True)
    unclaimed_seniors = senior_list.objects.filter(is_claimed=False)

    claimed_count = claimed_seniors.count()
    unclaimed_count = unclaimed_seniors.count()
    overall_count = claimed_count + unclaimed_count

    return render(request, 'claim_summary_page.html', {
        'claimed_count': claimed_count,
        'unclaimed_count': unclaimed_count,
        'overall_count': overall_count,
    })


def download_summary(request):
    current_datetime = timezone.now()
    formatted_datetime = current_datetime.strftime('%Y-%m-%d')
    filename = f"summary_{formatted_datetime}.csv"

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    writer = csv.writer(response)

    writer.writerow(['Claimed Seniors'])
    writer.writerow(['Last Name', 'First Name', 'Age', 'OSCA ID', 'Claimed Date', 'Status'])
    claimed_seniors = senior_list.objects.filter(is_claimed=True).order_by('last_name')
    for senior in claimed_seniors:
        claimed_status = 'Claimed'
        claimed_date = senior.claimed_date.strftime('%B %d, %Y')
        writer.writerow([
            senior.last_name,
            senior.first_name,
            senior.age,
            senior.OSCA_ID,
            claimed_date,
            claimed_status
        ])

    writer.writerow([])
    writer.writerow(['Unclaimed Seniors'])
    writer.writerow(['Last Name', 'First Name', 'Age', 'OSCA ID', 'Claimed Date', 'Status'])
    unclaimed_seniors = senior_list.objects.filter(is_claimed=False).order_by('last_name')
    for senior in unclaimed_seniors:
        claimed_status = 'Unclaimed'
        claimed_date = senior.claimed_date.strftime('%B %d, %Y')
        writer.writerow([
            senior.last_name,
            senior.first_name,
            senior.age,
            senior.OSCA_ID,
            claimed_date,
            claimed_status
        ])

    senior_list.objects.update(is_claimed=False)
    return response

def sms(request):
    if request.method == 'POST':
        phone_number = request.POST.get('phone_number')  # User input for phone number
        body_message = request.POST.get('body_message')  # User input for the message

        account_sid = settings.TWILIO_ACCOUNT_SID
        auth_token = settings.TWILIO_AUTH_TOKEN
        twilio_phone_number = settings.TWILIO_PHONE_NUMBER

        client = Client(account_sid, auth_token)

        try:
            message = client.messages.create(
                body=body_message,  # Use the retrieved message from the form
                from_=twilio_phone_number,
                to=phone_number
            )
            return JsonResponse({'status': 'Message sent successfully! SID: ' + message.sid})
        except Exception as e:
            return JsonResponse({'status': 'Failed to send message. Error: ' + str(e)})
        
    return render(request, 'sms.html')


def preview(request, id):
    seniors = senior_list.objects.get(id=id)
    return render(request, 'preview.html', {'seniors': seniors})

def camera(request):
    return render(request, 'capture_image.html')

@csrf_exempt
def capture_image(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body.decode('utf-8'))
            image_data = data.get('image_data', '')

            image_data = base64.b64decode(image_data.split(',')[1])
            nparr = np.frombuffer(image_data, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            filename = f"captured_image_{timestamp}.jpg"
            filepath = os.path.join(settings.MEDIA_ROOT, filename)
            cv2.imwrite(filepath, img)

            return JsonResponse({'image_path': filepath})

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Invalid request method.'}, status=400)



@csrf_exempt
def facial_recognition(request, id):
    seniors = senior_list.objects.get(id=id)

    if request.method == 'POST':
        captured_image_data_url = request.POST.get('captured_image', '')
        
        _, captured_image_base64 = captured_image_data_url.split(',')
        captured_image = np.frombuffer(base64.b64decode(captured_image_base64), np.uint8)

        captured_image_np = cv2.imdecode(captured_image, -1)

        if captured_image_np is None:
            return JsonResponse({'error': 'Unable to load the image.'})

        known_face_encoding = get_known_face_encoding(seniors.senior_image.path)

        face_locations = face_recognition.face_locations(captured_image_np)
        captured_face_encodings = face_recognition.face_encodings(captured_image_np, face_locations)

        for captured_face_encoding in captured_face_encodings:
            match = compare_faces(known_face_encoding, captured_face_encoding)

            if match:
                return JsonResponse({'match': True})
    
    return JsonResponse({'match': False})

def get_known_face_encoding(image_path):

    known_image = face_recognition.load_image_file(image_path)

    known_face_encoding = face_recognition.face_encodings(known_image)

    if known_face_encoding:
        return known_face_encoding[0] 
    else:
        return None

def compare_faces(known_encoding, captured_encoding):
    threshold = 0.5
    distance = face_recognition.face_distance([known_encoding], captured_encoding)

    return distance <= threshold





def camera_page(request, id):
    seniors = senior_list.objects.get(id=id)
    return render(request, 'camera.html', {'seniors': seniors})

def match(request, id):
    seniors = senior_list.objects.get(id=id)
    return render(request, 'match.html', {'seniors': seniors})

def unmatch(request, id):
    seniors = senior_list.objects.get(id=id)
    return render(request, 'unmatch.html', {'seniors': seniors})

