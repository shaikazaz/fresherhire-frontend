from rest_framework import generics,status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Notification
from .serializers import NotificationSerializer

class NotificationListView(generics.ListAPIView):
    serializer_class=NotificationSerializer
    def get_queryset(self): return Notification.objects.filter(user=self.request.user)

class UnreadCountView(APIView):
    def get(self,request): return Response({"count":Notification.objects.filter(user=request.user,is_read=False).count()})

class MarkReadView(APIView):
    def post(self,request,pk):
        n=Notification.objects.filter(pk=pk,user=request.user).first()
        if not n: return Response({"detail":"Notification not found."},status=404)
        n.is_read=True;n.save(update_fields=["is_read"])
        return Response(NotificationSerializer(n).data)

class MarkAllReadView(APIView):
    def post(self,request):
        count=Notification.objects.filter(user=request.user,is_read=False).update(is_read=True)
        return Response({"updated":count})
