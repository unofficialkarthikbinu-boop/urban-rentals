from django.urls import path
from . import views

urlpatterns = [
    path('start_chat/<int:vendor_id>/', views.start_chat, name='start_chat'),
    path('chats/', views.list_chats, name='list_chats'),
    path('chat/<int:room_id>/', views.chat_room, name='chat_room'),
    path('send_message/<int:room_id>/', views.send_message, name='send_message'),
    path('get_messages/<int:room_id>/', views.get_messages, name='get_messages'),
]