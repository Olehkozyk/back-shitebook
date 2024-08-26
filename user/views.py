from rest_framework.permissions import AllowAny
from django_filters import rest_framework as filters
from rest_framework.permissions import IsAuthenticated
from .filters import UserFilter
from .models import UserProfile, FriendRequest, UserFriend, Chat
from django.contrib.auth import get_user_model
from rest_framework.response import Response
from django.contrib.auth.models import User
from .pagination import CustomPaginationUsers
from .serializers import (
    LoginSerializer,
    RegisterSerializer,
    UserSerializer,
    FriendRequestSerializer,
)
from rest_framework import status, generics

UserModel = get_user_model()


class UserLoginView(generics.GenericAPIView):
    permission_classes = (AllowAny,)
    serializer_class = LoginSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            data = serializer.validated_data
            return Response({'status': True, 'data': data}, status=status.HTTP_200_OK)
        else:
            return Response({'status': False, 'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class UserRegisterView(generics.CreateAPIView):
    permission_classes = (AllowAny,)
    serializer_class = RegisterSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            data = serializer.save()
            response_data = {'status': True, 'data': data}
            return Response(response_data, status=status.HTTP_201_CREATED)
        else:
            response_data = {'status': False, 'errors': serializer.errors}
            print(serializer.errors)
            return Response(response_data, status=status.HTTP_400_BAD_REQUEST)


class IsFriendView(generics.GenericAPIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        user_id = request.query_params.get('user_id')
        current_user = request.user

        if not user_id:
            return Response({'status': False, 'error': 'User ID is required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({'status': False, 'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

        is_friend = current_user.user_friends.friends.filter(id=user.id).exists()

        return Response({'status': True, 'is_friend': is_friend}, status=status.HTTP_200_OK)


class RemoveFriendView(generics.GenericAPIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        user_id = request.data.get('user_id')
        current_user = request.user

        if not user_id:
            return Response({'status': False, 'error': 'User ID is required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user_to_remove = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({'status': False, 'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

        try:
            # Check if user_to_remove is indeed a friend of the current_user
            if not current_user.user_friends.friends.filter(id=user_to_remove.id).exists():
                return Response({'status': False, 'error': 'User is not a friend'}, status=status.HTTP_400_BAD_REQUEST)

            # Remove the friendship from both users
            current_user.user_friends.friends.remove(user_to_remove)
            user_to_remove.user_friends.friends.remove(current_user)

            chat = Chat.objects.filter(participants=current_user).filter(participants=user_to_remove).first()
            if chat:
                chat.delete()

        except Exception as e:
            # Log the exception for debugging
            print(f"Error removing friend: {e}")
            return Response({'status': False, 'error': f'Internal server error: {str(e)}'},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({'status': True, 'message': 'Friend removed successfully'}, status=status.HTTP_200_OK)


class AcceptFriendRequestView(generics.GenericAPIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        from_user_id = request.data.get('from_user_id')
        to_user = request.user

        if not from_user_id:
            return Response({'status': False, 'error': 'From user ID is required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            from_user = User.objects.get(id=from_user_id)
            friend_request = FriendRequest.objects.get(from_user=from_user, to_user=to_user)
        except User.DoesNotExist:
            return Response({'status': False, 'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        except FriendRequest.DoesNotExist:
            return Response({'status': False, 'error': 'Friend request not found'}, status=status.HTTP_404_NOT_FOUND)

        friend_request.accept()

        return Response({'status': True, 'message': 'Friend request accepted and deleted'}, status=status.HTTP_200_OK)


class UserAddFriendView(generics.GenericAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = FriendRequestSerializer

    def post(self, request, *args, **kwargs):
        to_user_id = request.data.get('user_id')
        if not to_user_id:
            return Response({'status': False, 'error': 'User ID is required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            to_user = User.objects.get(id=to_user_id)
        except User.DoesNotExist:
            return Response({'status': False, 'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

        from_user = request.user

        if FriendRequest.objects.filter(from_user=from_user, to_user=to_user).exists():
            return Response({'status': False, 'error': 'Request already exists'}, status=status.HTTP_200_OK)

        friend_request = FriendRequest.objects.create(from_user=from_user, to_user=to_user)
        serializer = self.get_serializer(friend_request)

        return Response({'status': True, 'data': serializer.data}, status=status.HTTP_201_CREATED)


class SentFriendRequestsView(generics.ListAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = FriendRequestSerializer

    def get_queryset(self):
        return FriendRequest.objects.filter(to_user=self.request.user)

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response({'status': True, 'data': serializer.data})


class FriendListView(generics.ListAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = UserSerializer

    def get_queryset(self):
        user = self.request.user
        try:
            user_friend = UserFriend.objects.get(user=user)
            friends = user_friend.friends.all()
        except UserFriend.DoesNotExist:
            friends = User.objects.none()
        return friends

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response({'status': True, 'data': serializer.data})


class UserRemoveFriendRequestView(generics.GenericAPIView):
    permission_classes = (IsAuthenticated,)

    def delete(self, request, *args, **kwargs):
        to_user_id = request.data.get('user_id')
        from_user_send = request.data.get('from_user')

        if not to_user_id:
            return Response({'status': False, 'error': 'User ID is required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user1 = User.objects.get(id=to_user_id)
        except User.DoesNotExist:
            return Response({'status': False, 'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

        user2 = request.user
        from_user = user1
        to_user = user2
        if from_user_send:
            from_user = user2
            to_user = user1

        try:
            friend_request = FriendRequest.objects.get(from_user=from_user, to_user=to_user)
        except FriendRequest.DoesNotExist:
            return Response({'status': False, 'error': 'Friend request not found'}, status=status.HTTP_404_NOT_FOUND)

        friend_request.delete()

        return Response({'status': True, 'message': 'Friend request deleted successfully'}, status=status.HTTP_200_OK)


class UserDetailView(generics.RetrieveAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = UserSerializer

    def get(self, request, *args, **kwargs):
        user_id = kwargs.get('pk')
        try:
            user = User.objects.select_related('profile').get(id=user_id)
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

        serializer = self.get_serializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)


class CurrentUserDetailView(generics.RetrieveAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = UserSerializer

    def get(self, request, *args, **kwargs):
        serializer = self.get_serializer(request.user)
        return Response({'status': True, 'data': serializer.data}, status=status.HTTP_200_OK)


class UserListView(generics.ListAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = UserSerializer
    pagination_class = CustomPaginationUsers
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = UserFilter

    def get_queryset(self):
        current_user = self.request.user
        return User.objects.all().select_related('profile').exclude(id=current_user.id).order_by('id')
