from django.conf import settings


DEFAULT_PROFILE_IMAGE_NAME = 'profiles/default.svg'


def build_media_url(name, request=None):
    url = f'{settings.MEDIA_URL}{name.lstrip("/")}'
    return request.build_absolute_uri(url) if request else url


def get_profile_image_url(profile, request=None):
    image = getattr(profile, 'image', None)
    if image:
        try:
            if image.name and image.storage.exists(image.name):
                url = image.url
                return request.build_absolute_uri(url) if request else url
        except (OSError, ValueError):
            pass
    return build_media_url(DEFAULT_PROFILE_IMAGE_NAME, request)
