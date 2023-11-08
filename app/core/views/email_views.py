from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from core.models import Node
from core.tasks import send_email_with_qr
from core.views.network_views import BaseAPIView


class NodeQRCodeView(BaseAPIView):
    def post(self, request, *args, **kwargs):
        try:
            node_id = request.data['node_id']
            employee = request.user.employee
            node = Node.objects.filter(employees=employee).get(pk=node_id)
        except KeyError:
            return Response({'status': 'No node_id provided.'}, status=status.HTTP_400_BAD_REQUEST)
        except Node.DoesNotExist:
            return Response({'status': 'Node does not exist.'}, status=status.HTTP_404_NOT_FOUND)

        contact = node.contacts
        if contact:
            data = f"Email: {contact.email}, Address: {contact.address}, Node: {node.name}"
            send_email_with_qr.delay(employee.user.email, data)
            return Response({'status': 'QR code sent.'}, status=status.HTTP_200_OK)
        else:
            return Response({'status': 'Contacts for this Node do not exist.'}, status=status.HTTP_404_NOT_FOUND)
