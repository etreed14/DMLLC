from unittest.mock import Mock
import importlib

class FakeSpeechClient:
    def long_running_recognize(self, config=None, audio=None):
        op = Mock()
        op.result.return_value = Mock(**{'_pb': Mock()})
        return op

class FakeStorageClient:
    def __init__(self):
        self.bucket_obj = Mock()
    def bucket(self, name):
        return self.bucket_obj

def test_transcribe_audio(monkeypatch, tmp_path):
    monkeypatch.setenv('GOOGLE_APPLICATION_CREDENTIALS', str(tmp_path/'creds.json'))
    (tmp_path/'creds.json').write_text('{}')
    monkeypatch.setattr('google.cloud.storage.Client', lambda *a, **k: FakeStorageClient())
    import pipeline.format_transcript as ft
    import sys
    sys.modules['format_transcript'] = ft
    import pipeline.transcribe_audio as ta
    monkeypatch.setattr(ta.speech, 'SpeechClient', lambda: FakeSpeechClient())
    monkeypatch.setattr(ta.storage, 'Client', lambda: FakeStorageClient())
    monkeypatch.setattr(ta, 'format_transcript', Mock(flatten_word_info=lambda x:[], format_transcript=lambda x:''))
    event = {'bucket':'b','name':ta.AUDIO_PREFIX + 'file.mp3'}
    ctx = None
    ta.transcribe_audio(event, ctx)

