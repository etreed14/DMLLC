from unittest.mock import Mock


class FakeBlob:
    def __init__(self):
        self.data = None

    def upload_from_string(self, data):
        self.data = data


class FakeBucket:
    def __init__(self):
        self.blobs = {}

    def blob(self, name):
        b = self.blobs.setdefault(name, FakeBlob())
        return b


class FakeClient:
    def __init__(self):
        self.buckets = {}

    def bucket(self, name):
        return self.buckets.setdefault(name, FakeBucket())


def test_transcribe_endpoint(monkeypatch, tmp_path):
    monkeypatch.setenv('GOOGLE_APPLICATION_CREDENTIALS', str(tmp_path/'creds.json'))
    (tmp_path/'creds.json').write_text('{}')
    monkeypatch.setattr('google.cloud.storage.Client', lambda *a, **k: FakeClient())
    import dmllc.main as main
    main.storage_client = FakeClient()
    monkeypatch.setattr(
        main.requests,
        'get',
        lambda *a, **k: Mock(json=lambda: {'access_token': 'tok'}),
    )
    resp_mock = Mock(
        status_code=200,
        json=lambda: {'results': [{'alternatives': [{'transcript': 'hi'}]}]},
    )
    monkeypatch.setattr(main.requests, 'post', lambda *a, **k: resp_mock)

    client = main.app.test_client()
    rv = client.post(
        '/transcribe',
        json={'bucket': 'b', 'name': 'file.mp3'},
    )
    assert rv.status_code == 200
    bucket = main.storage_client.bucket(main.OUTPUT_BUCKET)
    assert 'transcripts/file.txt' in bucket.blobs
