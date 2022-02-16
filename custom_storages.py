# telling django that in production we want to use s3 to store our static files whenever someone runs collectstatic.
# And that we want any uploaded product images to go there also.
from django.conf import settings
from storages.backends.s3boto3 import S3Boto3Storage


class StaticStorage(S3Boto3Storage):
    location = settings.STATICFILES_LOCATION  # to store static files


class MediaStorage(S3Boto3Storage):
    location = settings.MEDIAFILES_LOCATION  # to store media files
