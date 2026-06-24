from rest_framework import serializers

from .models import Notification


class NotificationSerializer(serializers.ModelSerializer):
    type_label = serializers.CharField(source='get_notification_type_display', read_only=True)
    actor_name = serializers.SerializerMethodField()

    class Meta:
        model = Notification
        fields = (
            'id',
            'notification_type',
            'type_label',
            'title',
            'message',
            'actor',
            'actor_name',
            'target_route',
            'target_params',
            'target_query',
            'is_read',
            'read_at',
            'created_at',
        )
        read_only_fields = fields

    def get_actor_name(self, obj):
        if not obj.actor:
            return ''
        profile = getattr(obj.actor, 'profile', None)
        if profile and profile.nickname:
            return profile.nickname
        return obj.actor.name or obj.actor.username
