from rest_framework import serializers
from .models import Comment, Pin, Save, History
from apps.user.models import User


class UserAvatarSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('username', 'avatar')


class PinSerializer(serializers.ModelSerializer):
    creator = UserAvatarSerializer()
    class Meta:
        model = Pin
        fields = '__all__'

class PinCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Pin
        fields = '__all__'
class PinSaveSerializer(serializers.ModelSerializer):

    class Meta:
        model = Save
        fields = '__all__'


class CommentCreatorSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'avatar', 'username')

class CommentPostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = "__all__"


class CommentSerializer(serializers.ModelSerializer):
    creator = CommentCreatorSerializer() 
    class Meta:
        model = Comment
        fields = '__all__'

class PinCommentSerializer(serializers.ModelSerializer):
    comment_set = CommentSerializer(many=True)
    class Meta:
        model = Pin
        fields = ('id', 'comment_set')


class HistoryPostSerializer(serializers.ModelSerializer):
    class Meta:
        model = History
        fields = '__all__'


class HistoryGetSerializer(serializers.ModelSerializer):
    pin = PinSerializer()

    class Meta:
        model = History
        fields = '__all__'