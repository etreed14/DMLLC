import logging
from pipeline.main import gcs_event as _gcs_event, http_trigger as _http_trigger
logger = logging.getLogger(__name__)
def gcs_event(event, context=None): return _gcs_event(event, context)
def http_trigger(request): return _http_trigger(request)
