"""Security tests for stdlib archive safe-extraction (B2 hardening)."""
from __future__ import annotations

import io
import os
import tarfile
import tempfile
import unittest
import zipfile

from stdlib.archive import tar_extract, zip_extract


def _write_file(dirpath: str, name: str, data: bytes) -> str:
    path = os.path.join(dirpath, name)
    with open(path, "wb") as f:
        f.write(data)
    return path


class TestSafeExtract(unittest.TestCase):
    """Zip/tar extraction must reject traversal and link members."""

    def test_zip_rejects_path_traversal(self):
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w") as zf:
            zf.writestr("../evil.txt", "pwned")
        with tempfile.TemporaryDirectory() as tmp:
            archive = _write_file(tmp, "evil.zip", buf.getvalue())
            with self.assertRaises(ValueError):
                zip_extract(archive, tmp)

    def test_zip_extract_ok(self):
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w") as zf:
            zf.writestr("ok.txt", "fine")
        with tempfile.TemporaryDirectory() as tmp:
            archive = _write_file(tmp, "ok.zip", buf.getvalue())
            zip_extract(archive, tmp)
            self.assertTrue(os.path.isfile(os.path.join(tmp, "ok.txt")))

    def test_tar_rejects_path_traversal(self):
        buf = io.BytesIO()
        with tarfile.open(fileobj=buf, mode="w") as tf:
            info = tarfile.TarInfo("../evil.txt")
            data = b"pwned"
            info.size = len(data)
            tf.addfile(info, io.BytesIO(data))
        with tempfile.TemporaryDirectory() as tmp:
            archive = _write_file(tmp, "evil.tgz", buf.getvalue())
            with self.assertRaises(ValueError):
                tar_extract(archive, tmp)

    def test_tar_rejects_symlink(self):
        buf = io.BytesIO()
        with tarfile.open(fileobj=buf, mode="w") as tf:
            link = tarfile.TarInfo("link")
            link.type = tarfile.SYMTYPE
            link.linkname = "/etc/passwd"
            tf.addfile(link)
        with tempfile.TemporaryDirectory() as tmp:
            archive = _write_file(tmp, "link.tgz", buf.getvalue())
            with self.assertRaises(ValueError):
                tar_extract(archive, tmp)

    def test_tar_extract_ok(self):
        buf = io.BytesIO()
        with tarfile.open(fileobj=buf, mode="w") as tf:
            info = tarfile.TarInfo("ok.txt")
            data = b"fine"
            info.size = len(data)
            tf.addfile(info, io.BytesIO(data))
        with tempfile.TemporaryDirectory() as tmp:
            archive = _write_file(tmp, "ok.tgz", buf.getvalue())
            tar_extract(archive, tmp)
            self.assertTrue(os.path.isfile(os.path.join(tmp, "ok.txt")))


class TestLegacyHashes(unittest.TestCase):
    """MD5/SHA-1 helpers must still produce stable digests."""

    def test_md5(self):
        from stdlib.crypto import hash_md5
        self.assertEqual(hash_md5(b"abc"), "900150983cd24fb0d6963f7d28e17f72")

    def test_sha1(self):
        from stdlib.crypto import hash_sha1
        self.assertEqual(hash_sha1(b"abc"), "a9993e364706816aba3e25717850c26c9cd0d89d")


if __name__ == "__main__":
    unittest.main()
