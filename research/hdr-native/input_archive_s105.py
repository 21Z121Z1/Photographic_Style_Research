"""Bounded, resumable range access to four existing authenticated ciphers.

Only GitHub -> macOS runner. Every consumed cipher is SHA-checked and fully GPG
authenticated by the unchanged S103 decryptor; skipped ZIP bytes are not claimed
to have been downloaded or rehashed. Never fall back to an unsolicited full200.
"""
import io
import json
import os
import shutil
import time
import urllib.error
import urllib.request
from input_archive_s103 import API, ZIP_BYTES, ZIP_SHA, SOURCE_RUN, NoRedirect, decrypt_photo

class RangeArtifact(io.RawIOBase):
    BLOCK = 8 * 1024 * 1024
    GUARD = 3_000_000_000

    def __init__(self, folder):
        super().__init__()
        assert shutil.disk_usage(folder).free > 5_000_000_000
        self.position = 0
        self.cache_start = 0
        self.cache = b''
        self.received = 0
        self.requested = 0
        self.successful_ranges = 0
        self.retried_ranges = 0
        self.url = None
        self.refreshes = 0
        self.refresh()

    def refresh(self):
        headers = {'Authorization': 'Bearer ' + os.environ['GH_TOKEN'], 'Accept': 'application/vnd.github+json', 'X-GitHub-Api-Version': '2022-11-28'}
        with urllib.request.urlopen(urllib.request.Request(API, headers=headers), timeout=60) as response:
            metadata = json.load(response)
        assert not metadata['expired'] and metadata['size_in_bytes'] == ZIP_BYTES
        assert metadata['digest'] == 'sha256:' + ZIP_SHA
        self.expires = metadata['expires_at']
        opener = urllib.request.build_opener(NoRedirect)
        try:
            response = opener.open(urllib.request.Request(API + '/zip', headers=headers), timeout=60)
        except urllib.error.HTTPError as response:
            assert response.code == 302
            location = response.headers['Location']
        else:
            response.close()
            raise RuntimeError('Expected signed artifact redirect')
        assert location.startswith('https://')
        self.url = location
        self.refreshes += 1

    def readable(self):
        return True

    def seekable(self):
        return True

    def tell(self):
        return self.position

    def seek(self, offset, whence=0):
        target = offset if whence == 0 else self.position + offset if whence == 1 else ZIP_BYTES + offset if whence == 2 else None
        if target is None or target < 0 or target > ZIP_BYTES:
            raise ValueError('Invalid artifact seek')
        self.position = target
        return target

    def fetch_range(self, start, stop):
        assert 0 <= start < stop <= ZIP_BYTES and stop - start <= self.BLOCK
        for attempt in range(4):
            self.requested += stop - start
            assert self.requested <= self.GUARD, 'Range request budget exhausted; no full fallback'
            try:
                request = urllib.request.Request(self.url, headers={'Range': f'bytes={start}-{stop-1}'})
                with urllib.request.urlopen(request, timeout=45) as response:
                    # Check before reading the body; a server ignoring Range may
                    # otherwise silently send the complete2GB artifact again.
                    if response.status != 206:
                        raise ValueError('Artifact server did not honor Range; full200 refused')
                    assert response.headers['Content-Range'] == f'bytes {start}-{stop-1}/{ZIP_BYTES}'
                    assert int(response.headers['Content-Length']) == stop - start
                    result = bytearray()
                    while len(result) < stop - start:
                        chunk = response.read(min(1024 * 1024, stop - start - len(result)))
                        if not chunk:
                            raise OSError('Incomplete artifact range')
                        self.received += len(chunk)
                        result.extend(chunk)
                    assert not response.read(1)
                self.successful_ranges += 1
                return bytes(result)
            except urllib.error.HTTPError as error:
                if error.code == 403 and attempt < 3:
                    self.refresh()
                elif error.code not in [408, 429, 500, 502, 503, 504] or attempt == 3:
                    raise RuntimeError('Artifact range HTTP failure ' + str(error.code)) from None
            except (TimeoutError, OSError, urllib.error.URLError):
                if attempt == 3:
                    raise RuntimeError('Artifact range transport failed after four bounded attempts') from None
            self.retried_ranges += 1
            time.sleep(1 + attempt)
        raise RuntimeError('Range fetch did not complete')

    def read(self, size=-1):
        assert not self.closed
        if size is None or size < 0:
            size = ZIP_BYTES - self.position
        end = min(ZIP_BYTES, self.position + size)
        parts = []
        while self.position < end:
            if not self.cache_start <= self.position < self.cache_start + len(self.cache):
                self.cache_start = self.position // self.BLOCK * self.BLOCK
                stop = min(ZIP_BYTES, self.cache_start + self.BLOCK)
                self.cache = self.fetch_range(self.cache_start, stop)
            amount = min(end - self.position, self.cache_start + len(self.cache) - self.position)
            offset = self.position - self.cache_start
            parts.append(self.cache[offset:offset + amount])
            self.position += amount
        return b''.join(parts)

    def receipt(self):
        return {'source_run_id': SOURCE_RUN, 'artifact_id': 12310032763, 'declared_ZIP_bytes': ZIP_BYTES, 'declared_provider_ZIP_sha256': ZIP_SHA, 'whole_ZIP_rehashed_on_this_runner': False, 'each_consumed_cipher_SHA256_and_full_GPG_checked': True, 'received_body_bytes': self.received, 'requested_range_bytes_including_retries': self.requested, 'successful_ranges': self.successful_ranges, 'retried_ranges': self.retried_ranges, 'signed_URL_refreshes': self.refreshes, 'range_block_max_bytes': self.BLOCK, 'request_guard_bytes': self.GUARD, 'route': 'GitHub to macOS runner only; no Japan/HK image backhaul', 'expires_at_observed': self.expires, 'counts_exclude_HTTP_transport_overhead': True, 'full200_fallback_allowed': False}

    def close(self):
        self.cache = b''
        self.url = None
        super().close()

def download(scratch):
    archive = RangeArtifact(scratch)
    return archive, archive.receipt()
