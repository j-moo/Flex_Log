from django.utils import timezone

from .models import Notification


def get_display_name(user):
    profile = getattr(user, 'profile', None)
    if profile and profile.nickname:
        return profile.nickname
    return user.name or user.username


def create_notification(
    *,
    user,
    notification_type,
    title,
    message,
    actor=None,
    target_route='',
    target_params=None,
    target_query=None,
    dedupe_key='',
):
    if not user:
        return None
    if actor and actor.id == user.id:
        return None
    if dedupe_key:
        existing = Notification.objects.filter(user=user, dedupe_key=dedupe_key).first()
        if existing:
            return existing

    return Notification.objects.create(
        user=user,
        actor=actor,
        notification_type=notification_type,
        title=title,
        message=message,
        target_route=target_route,
        target_params=target_params or {},
        target_query=target_query or {},
        dedupe_key=dedupe_key,
    )


def upsert_grouped_notification(
    *,
    user,
    notification_type,
    title,
    message,
    actor=None,
    target_route='',
    target_params=None,
    target_query=None,
    dedupe_key='',
):
    if not user:
        return None
    if actor and actor.id == user.id:
        return None
    if not dedupe_key:
        return create_notification(
            user=user,
            actor=actor,
            notification_type=notification_type,
            title=title,
            message=message,
            target_route=target_route,
            target_params=target_params,
            target_query=target_query,
        )

    notification = Notification.objects.filter(user=user, dedupe_key=dedupe_key).first()
    if not notification:
        return create_notification(
            user=user,
            actor=actor,
            notification_type=notification_type,
            title=title,
            message=message,
            target_route=target_route,
            target_params=target_params,
            target_query=target_query,
            dedupe_key=dedupe_key,
        )

    notification.actor = actor
    notification.notification_type = notification_type
    notification.title = title
    notification.message = message
    notification.target_route = target_route
    notification.target_params = target_params or {}
    notification.target_query = target_query or {}
    notification.is_read = False
    notification.read_at = None
    notification.created_at = timezone.now()
    notification.save(
        update_fields=(
            'actor',
            'notification_type',
            'title',
            'message',
            'target_route',
            'target_params',
            'target_query',
            'is_read',
            'read_at',
            'created_at',
        ),
    )
    return notification
