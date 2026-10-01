"""Only for collecting static assets in an image build; never run the server with this."""

from .test import *

STORAGES["staticfiles"] = {"BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage"}
