from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from GuestApp.models import tbl_customer, tbl_vendor
from .models import ChatRoom, Message
from django.utils import timezone
from django.db.models import Q
from django.views.decorators.csrf import csrf_exempt

def start_chat(request, vendor_id):
    if 'customer' not in request.session:
        return redirect('login')
    
    try:
        # Assuming session stores login_id, we need to find customer by login_id
        customer = tbl_customer.objects.get(login__login_id=request.session['customer'])
    except tbl_customer.DoesNotExist:
        # Fallback 
        return redirect('login')
             
    vendor = get_object_or_404(tbl_vendor, vendor_id=vendor_id)
    
    # Check if chat room exists
    chat_room, created = ChatRoom.objects.get_or_create(customer=customer, vendor=vendor)
    
    return redirect('chat_room', room_id=chat_room.id)

def list_chats(request):
    """View to list all active chats for the logged-in user"""
    context = {}
    if 'customer' in request.session:
        try:
            customer = tbl_customer.objects.get(login__login_id=request.session['customer'])
        except tbl_customer.DoesNotExist:
             return redirect('login')
             
        chats = ChatRoom.objects.filter(customer=customer).order_by('-updated_at')
        context['user_type'] = 'customer'
        context['chats'] = chats
        return render(request, 'ChatApp/chat_list_customer.html', context)
        
    elif 'vendor' in request.session:
        try:
            vendor = tbl_vendor.objects.get(login__login_id=request.session['vendor'])
        except tbl_vendor.DoesNotExist:
            return redirect('vendor_home')
            
        chats = ChatRoom.objects.filter(vendor=vendor).order_by('-updated_at')
        context['user_type'] = 'vendor'
        context['chats'] = chats
        return render(request, 'ChatApp/chat_list_vendor.html', context)
    else:
        return redirect('login')

def chat_room(request, room_id):
    chat_room = get_object_or_404(ChatRoom, id=room_id)
    
    # Check permission
    is_customer = 'customer' in request.session
    is_vendor = 'vendor' in request.session
    
    if is_customer:
        try:
            customer = tbl_customer.objects.get(login__login_id=request.session['customer'])
        except tbl_customer.DoesNotExist:
            return redirect('login')
            
        if chat_room.customer != customer:
            return redirect('customer_home')
            
        context = {
            'chat_room': chat_room, 
            'user_type': 'customer',
            'other_user_name': chat_room.vendor.name, 
            'other_user_image': None
        }
        return render(request, 'ChatApp/chat_room.html', context)
        
    elif is_vendor:
        try:
            vendor = tbl_vendor.objects.get(login__login_id=request.session['vendor'])
        except tbl_vendor.DoesNotExist:
            return redirect('vendor_home')
            
        if chat_room.vendor != vendor:
            return redirect('vendor_home')
            
        context = {
            'chat_room': chat_room, 
            'user_type': 'vendor',
            'other_user_name': chat_room.customer.name, 
            'other_user_image': chat_room.customer.id_proof.url if chat_room.customer.id_proof else None
        }
        return render(request, 'ChatApp/chat_room.html', context)
    else:
        return redirect('login')

def send_message(request, room_id):
    if request.method == 'POST':
        chat_room = get_object_or_404(ChatRoom, id=room_id)
        content = request.POST.get('content')
        
        if not content:
            return JsonResponse({'status': 'error', 'message': 'Empty message'})
            
        sender_type = None
        
        # Check if the user is the customer for this room
        if 'customer' in request.session:
            try:
                session_val = str(request.session['customer'])
                if session_val == str(chat_room.customer.login.login_id) or session_val == str(chat_room.customer.customer_id):
                    sender_type = 'customer'
            except:
                pass

        # Check if the user is the vendor for this room (if not identified as customer)
        if not sender_type and 'vendor' in request.session:
            try:
                session_val = str(request.session['vendor'])
                if session_val == str(chat_room.vendor.login.login_id) or session_val == str(chat_room.vendor.vendor_id):
                    sender_type = 'vendor'
            except:
                pass
        
        # Fallback
        if not sender_type:
            if 'customer' in request.session:
                 sender_type = 'customer'
            elif 'vendor' in request.session:
                 sender_type = 'vendor'
            else:
                 return JsonResponse({'status': 'error', 'message': 'Unauthorized'}, status=403)
            
        message = Message.objects.create(room=chat_room, sender_type=sender_type, content=content)
        chat_room.updated_at = timezone.now()
        chat_room.save()
        
        return JsonResponse({
            'status': 'success', 
            'message': {
                'id': message.id,
                'content': message.content,
                'timestamp': message.timestamp.strftime('%H:%M'),
                'sender_type': sender_type
            }
        })
    return JsonResponse({'status': 'error'}, status=400)

def get_messages(request, room_id):
    chat_room = get_object_or_404(ChatRoom, id=room_id)
    last_id = request.GET.get('last_id', 0)
    
    messages = Message.objects.filter(room=chat_room, id__gt=last_id).order_by('timestamp')
    
    data = []
    for msg in messages:
        data.append({
            'id': msg.id,
            'content': msg.content,
            'sender_type': msg.sender_type,
            'timestamp': msg.timestamp.strftime('%H:%M')
        })
        
        # Mark as read if receiving
        if 'customer' in request.session and msg.sender_type == 'vendor':
            if not msg.is_read:
                msg.is_read = True
                msg.save()
        elif 'vendor' in request.session and msg.sender_type == 'customer':
            if not msg.is_read:
                msg.is_read = True
                msg.save()
            
    return JsonResponse({'messages': data})
