import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch, Mock

from app.core.config import settings
from app.services.jobs import JobStore


class JobStorageSecurityTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.storage = self.root / "jobs"
        self.storage.mkdir()
        self.config = patch.object(settings, "storage_dir", self.storage)
        self.config.start()
        self.addCleanup(self.config.stop)
        self.addCleanup(self.temp.cleanup)
        self.store = JobStore()

    def test_hostile_filenames_are_rejected_before_any_job_is_created(self):
        for filename in (None, "", ".", "..", "../outside.wav", "nested/file.wav",
                         "..\\outside.wav", "C:\\outside.wav", "C:outside.wav",
                         "/tmp/outside.wav", "bad\x00.wav"):
            with self.subTest(filename=filename), self.assertRaises(ValueError):
                self.store.create_job(filename, b"audio")
        self.assertEqual(list(self.storage.iterdir()), [])

    def test_original_name_is_preserved_but_storage_name_is_server_owned(self):
        for filename in ("演奏 録音.wav", "job.json", "score.json"):
            with self.subTest(filename=filename):
                meta = self.store.create_job(filename, b"audio")
                folder = self.storage / meta["job_id"]
                self.assertEqual(meta["filename"], filename)
                self.assertEqual((folder / meta["input_filename"]).read_bytes(), b"audio")
                self.assertEqual(self.store.get_job(meta["job_id"]), meta)
                self.assertNotEqual(meta["input_filename"], "job.json")
                self.assertNotEqual(meta["input_filename"], "score.json")

    def test_job_identifier_cannot_escape_storage(self):
        for job_id in ("..", "../outside", "/tmp", "not-a-uuid"):
            with self.subTest(job_id=job_id), self.assertRaises(ValueError):
                self.store.get_job(job_id)

    def test_forged_output_path_cannot_read_another_job_or_external_file(self):
        first = self.store.create_job("first.wav", b"first")
        second = self.store.create_job("second.wav", b"second")
        folder = self.storage / first["job_id"]
        foreign = self.storage / second["job_id"] / second["input_filename"]
        outside = self.root / "private.txt"
        outside.write_text("private")
        for target in (foreign, outside):
            (folder / "job.json").write_text(json.dumps({**first, "drums_path": str(target)}))
            with self.subTest(target=target), self.assertRaises(ValueError):
                self.store.get_drums_path(first["job_id"])
        stem = folder / "separation" / "drums.wav"
        stem.parent.mkdir()
        stem.write_bytes(b"stem")
        (folder / "job.json").write_text(json.dumps({**first, "drums_path": str(stem)}))
        self.assertEqual(self.store.get_drums_path(first["job_id"]), stem.resolve())

    def test_symlinks_cannot_redirect_metadata_or_score_reads(self):
        meta = self.store.create_job("audio.wav", b"audio")
        folder = self.storage / meta["job_id"]
        outside = self.root / "private.json"
        outside.write_text('{"private":true}')
        (folder / "score.json").symlink_to(outside)
        with self.assertRaises(ValueError):
            self.store.get_score(meta["job_id"])
        (folder / "job.json").unlink()
        (folder / "job.json").symlink_to(outside)
        with self.assertRaises(ValueError):
            self.store.get_job(meta["job_id"])

    def test_processing_uses_contained_input_and_output_for_new_and_legacy_jobs(self):
        for legacy in (False, True):
            meta = self.store.create_job("演奏.wav", b"audio")
            folder = self.storage / meta["job_id"]
            if legacy:
                (folder / meta.pop("input_filename")).rename(folder / meta["filename"])
                (folder / "job.json").write_text(json.dumps(meta))
            stem = folder / "separation" / "drums.wav"
            def separate(input_path, output_dir):
                self.assertEqual(input_path.read_bytes(), b"audio")
                output_dir.mkdir()
                stem.write_bytes(b"stem")
                return Mock(drums_path=stem)
            engine = Mock(separate=separate)
            score = Mock(model_dump_json=Mock(return_value='{"score":true}'))
            with patch("app.services.jobs.get_separation_engine", return_value=engine), patch("app.services.jobs.analyze_drums_to_score", return_value=score):
                self.assertEqual(self.store.process_job(meta["job_id"])["status"], "done")
            self.assertEqual(self.store.get_score(meta["job_id"]), {"score": True})

    def test_processing_rejects_symlink_output_directory_before_engine_execution(self):
        meta = self.store.create_job("audio.wav", b"audio")
        folder = self.storage / meta["job_id"]
        (folder / "separation").symlink_to(self.root, target_is_directory=True)
        with patch("app.services.jobs.get_separation_engine") as factory, self.assertRaises(ValueError):
            self.store.process_job(meta["job_id"])
        factory.assert_not_called()


if __name__ == "__main__":
    unittest.main()
