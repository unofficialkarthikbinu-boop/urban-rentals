from django.db import models
from GuestApp.models import tbl_customer, tbl_vendor

class ChatRoom(models.Model):
    customer = models.ForeignKey(tbl_customer, on_delete=models.CASCADE, related_name='customer_chats')
    vendor = models.ForeignKey(tbl_vendor, on_delete=models.CASCADE, related_name='vendor_chats')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('customer', 'vendor')
        ordering = ['-updated_at']

    def __str__(self):
        return f"Chat: {self.customer.name} - {self.vendor.name}"

class Message(models.Model):
    room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name='messages')
    sender_type = models.CharField(max_length=10) # 'customer' or 'vendor'
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ['timestamp']

    def __str__(self):
        return f"{self.sender_type}: {self.content[:20]}..."
