"""Focused release-readiness coverage for AI runtime assets and providers."""

from __future__ import annotations

import importlib.util
import json
import logging
import sys
import tempfile
import types
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from backend.server.llm_providers.ollama_provider import (
    OllamaProvider,
    ollama_tags_url,
)


ROOT = Path(__file__).resolve().parents[1]


def _load_rag_module() -> types.ModuleType:
    """Load RAG code without importing the production service registry."""
    package_name = "release_rag_test_package"
    module_name = f"{package_name}.services.rag_service"
    if module_name in sys.modules:
        return sys.modules[module_name]

    package = types.ModuleType(package_name)
    package.__path__ = []
    services = types.ModuleType(f"{package_name}.services")
    services.__path__ = []
    config = types.ModuleType(f"{package_name}.config")
    config.Config = object
    sys.modules[package_name] = package
    sys.modules[services.__name__] = services
    sys.modules[config.__name__] = config

    spec = importlib.util.spec_from_file_location(
        module_name,
        ROOT / "backend/server/services/rag_service.py",
    )
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


class _Vectors:
    def __init__(self, count: int) -> None:
        self.shape = (count, 2)


class _Embedder:
    def encode(self, texts: list[str], **_kwargs: object) -> _Vectors:
        return _Vectors(len(texts))


class _Index:
    def __init__(self, _dimension: int) -> None:
        self.added = False

    def add(self, _vectors: _Vectors) -> None:
        self.added = True


class _Faiss:
    IndexFlatIP = _Index

    @staticmethod
    def write_index(_index: _Index, path: str) -> None:
        Path(path).write_bytes(b"release-test-index")

    @staticmethod
    def read_index(_path: str) -> _Index:
        return _Index(2)


def _rag_config(
    docs_dir: Path,
    index_dir: Path,
    *,
    auto_build: bool,
) -> SimpleNamespace:
    return SimpleNamespace(
        RAG_DOCS_DIR=str(docs_dir),
        RAG_INDEX_DIR=str(index_dir),
        RAG_EMBEDDING_MODEL="release-test-embedding",
        RAG_CHUNK_SIZE=120,
        RAG_CHUNK_OVERLAP=20,
        RAG_TOP_K=5,
        RAG_MIN_SCORE=0.3,
        RAG_AUTO_BUILD_ON_START=auto_build,
    )


def _bare_rag(module: types.ModuleType, config: SimpleNamespace) -> object:
    service = module.RAGService.__new__(module.RAGService)
    service.config = config
    service.docs_dir = Path(config.RAG_DOCS_DIR)
    service.index_dir = Path(config.RAG_INDEX_DIR)
    service.index_file = service.index_dir / "knowledge.faiss"
    service.metadata_file = service.index_dir / "metadata.json"
    service.manifest_file = service.index_dir / module.INDEX_MANIFEST_FILENAME
    service.embedding_model_name = config.RAG_EMBEDDING_MODEL
    service.embedder = _Embedder()
    service.faiss = _Faiss()
    service.index = None
    service.metadata = []
    service.last_build_report = None
    service.initialization_error = None
    return service


class RAGReleaseReadinessTests(unittest.TestCase):
    def test_manifest_detects_stale_sources_and_preserves_legacy_index(self) -> None:
        module = _load_rag_module()
        with tempfile.TemporaryDirectory() as temporary_directory:
            temporary = Path(temporary_directory)
            docs = temporary / "knowledge"
            index = temporary / "index"
            docs.mkdir()
            (docs / "approved.json").write_text(
                json.dumps({"title": "Approved record", "text": "Guidance services."}),
                encoding="utf-8",
            )
            (docs / "._approved.json").write_bytes(b"AppleDouble sidecar")
            (docs / "blank.txt").write_text("   ", encoding="utf-8")
            index.mkdir()
            (index / "knowledge.faiss").write_bytes(b"legacy")
            (index / "metadata.json").write_text("[]", encoding="utf-8")

            service = _bare_rag(module, _rag_config(docs, index, auto_build=True))
            with self.assertLogs(module.logger.name, logging.INFO) as logs:
                count = service.build_index()

            self.assertGreater(count, 0)
            self.assertTrue((index / "archive/legacy_pre_manifest/knowledge.faiss").is_file())
            self.assertTrue((index / "manifest.json").is_file())
            self.assertEqual(service.last_build_report.indexed_sources, ("approved.json",))
            self.assertNotIn(
                "._approved.json", service.last_build_report.discovered_sources
            )
            self.assertEqual(
                service.last_build_report.skipped_sources,
                ({"source": "blank.txt", "reason": "empty_or_invalid"},),
            )
            self.assertNotIn("Guidance services.", "\n".join(logs.output))

            current, reason = service._index_is_current()
            self.assertTrue(current, reason)

            (docs / "approved.json").write_text(
                json.dumps({"title": "Changed approved record", "text": "Different guidance."}),
                encoding="utf-8",
            )
            current, reason = service._index_is_current()
            self.assertFalse(current)
            self.assertEqual(reason, "source_fingerprint_mismatch")

    def test_stale_index_rebuilds_only_when_auto_build_is_enabled(self) -> None:
        module = _load_rag_module()
        with tempfile.TemporaryDirectory() as temporary_directory:
            temporary = Path(temporary_directory)
            docs = temporary / "knowledge"
            index = temporary / "index"
            docs.mkdir()
            source = docs / "approved.txt"
            source.write_text("Approved Guidance Office information.", encoding="utf-8")

            build_config = _rag_config(docs, index, auto_build=True)
            builder = _bare_rag(module, build_config)
            self.assertGreater(builder.build_index(), 0)
            source.write_text("Updated approved Guidance Office information.", encoding="utf-8")

            fake_faiss = types.SimpleNamespace(
                IndexFlatIP=_Index,
                write_index=_Faiss.write_index,
                read_index=_Faiss.read_index,
            )
            fake_sentence_transformers = types.SimpleNamespace(
                SentenceTransformer=lambda _name: _Embedder()
            )
            with patch.object(module, "Config", return_value=_rag_config(docs, index, auto_build=False)):
                with patch.dict(
                    sys.modules,
                    {"faiss": fake_faiss, "sentence_transformers": fake_sentence_transformers},
                ):
                    stale = module.RAGService()
            self.assertIsNone(stale.index)
            self.assertIn("RAG index is stale", stale.initialization_error)

            with patch.object(module, "Config", return_value=_rag_config(docs, index, auto_build=True)):
                with patch.dict(
                    sys.modules,
                    {"faiss": fake_faiss, "sentence_transformers": fake_sentence_transformers},
                ):
                    rebuilt = module.RAGService()
            self.assertIsNotNone(rebuilt.index)
            self.assertIsNone(rebuilt.initialization_error)
            self.assertTrue(rebuilt._index_is_current()[0])


class EmotionArtifactProvisioningTests(unittest.TestCase):
    @staticmethod
    def _module() -> types.ModuleType:
        spec = importlib.util.spec_from_file_location(
            "verify_emotion_model_release_test",
            ROOT / "backend/scripts/verify_emotion_model.py",
        )
        assert spec and spec.loader
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module

    def test_actual_controlled_artifact_matches_its_manifest(self) -> None:
        module = self._module()
        errors = module.verify_model_directory(
            ROOT / "ai_engine/models/english/latest"
        )
        self.assertEqual(errors, [])

    def test_missing_and_mismatched_artifacts_fail_clearly(self) -> None:
        module = self._module()
        with tempfile.TemporaryDirectory() as temporary_directory:
            model_dir = Path(temporary_directory)
            (model_dir / "runtime_artifact_manifest.json").write_text(
                json.dumps(
                    {
                        "required_files": {
                            "model.safetensors": {
                                "size_bytes": 4,
                                "sha256": "0" * 64,
                            }
                        }
                    }
                ),
                encoding="utf-8",
            )
            self.assertIn(
                "Missing required model file: model.safetensors",
                module.verify_model_directory(model_dir),
            )
            (model_dir / "model.safetensors").write_bytes(b"bad!")
            self.assertIn(
                "Checksum mismatch for model file: model.safetensors",
                module.verify_model_directory(model_dir),
            )

    def test_current_installation_and_deployment_docs_include_provisioning(self) -> None:
        for path in ("docs/INSTALLATION_GUIDE.md", "docs/06_deployment_guide.md"):
            content = (ROOT / path).read_text(encoding="utf-8")
            with self.subTest(path=path):
                self.assertIn("verify_emotion_model.py", content)
                self.assertIn("d90161c6b064d42ecee866e099f9f3125abb969e7a5ce76cd4c4fb32369ccce9", content)


class OllamaProviderReleaseTests(unittest.TestCase):
    def test_tags_endpoint_uses_the_configured_generation_base_url(self) -> None:
        expected = {
            "http://localhost:11434/api/generate": "http://localhost:11434/api/tags",
            "http://remote.example:11434/api/generate/": "http://remote.example:11434/api/tags",
            "https://ollama.example/service/api/generate": "https://ollama.example/service/api/tags",
            "https://ollama.example": "https://ollama.example/api/tags",
        }
        for generation_url, tags_url in expected.items():
            with self.subTest(generation_url=generation_url):
                self.assertEqual(ollama_tags_url(generation_url), tags_url)

    def test_probe_and_generation_use_configured_urls_without_network(self) -> None:
        configured_url = "https://ollama.example/service/api/generate/"
        configuration = SimpleNamespace(
            OLLAMA_URL=configured_url,
            OLLAMA_MODEL="controlled-model",
        )
        response = SimpleNamespace(
            status_code=200,
            raise_for_status=lambda: None,
            json=lambda: {"response": "safe"},
        )
        with patch(
            "backend.server.llm_providers.ollama_provider.Config",
            return_value=configuration,
        ):
            with patch(
                "backend.server.llm_providers.ollama_provider.requests.get",
                return_value=response,
            ) as get_request:
                provider = OllamaProvider()
            with patch(
                "backend.server.llm_providers.ollama_provider.requests.post",
                return_value=response,
            ) as post_request:
                result = provider.generate("safe test prompt")

        self.assertTrue(result.success)
        self.assertEqual(
            get_request.call_args.args[0],
            "https://ollama.example/service/api/tags",
        )
        self.assertEqual(post_request.call_args.args[0], configured_url)

    def test_unavailable_configured_ollama_server_fails_without_generation(self) -> None:
        configuration = SimpleNamespace(
            OLLAMA_URL="https://offline.example/api/generate",
            OLLAMA_MODEL="controlled-model",
        )
        with patch(
            "backend.server.llm_providers.ollama_provider.Config",
            return_value=configuration,
        ):
            with patch(
                "backend.server.llm_providers.ollama_provider.requests.get",
                side_effect=OSError("offline"),
            ):
                provider = OllamaProvider()

        self.assertFalse(provider.available)
        self.assertIn("offline", provider.initialization_error)


class ConversationFinalizationLoggingTests(unittest.TestCase):
    def test_finalization_logs_no_internal_identifier_or_protected_text(self) -> None:
        from backend.server.services import conversation_service

        protected_text = "PROTECTED-CONVERSATION-RELEASE-SENTINEL"
        identifiers = ("987654", "456789")
        summary = SimpleNamespace(
            primary_concern="safe",
            conversation_type="general",
            emotion="neutral",
            flagged=False,
            appointment_recommendation=False,
            recommendations="safe",
            suggested_intervention="safe",
            language="english",
            total_messages=1,
            summary="safe",
        )
        with patch.object(
            conversation_service.summary_service,
            "generate_summary",
            return_value=summary,
        ):
            with patch.object(
                conversation_service,
                "save_conversation_summary",
                return_value=456789,
            ):
                with self.assertLogs(conversation_service.logger.name, logging.INFO) as logs:
                    conversation_service.finalize_conversation(
                        user={"id": 987654, "full_name": protected_text},
                        conversation=[{"from": "user", "text": protected_text}],
                        topic="general",
                        language="english",
                        emotion="neutral",
                        flagged=False,
                    )

        output = "\n".join(logs.output)
        self.assertNotIn(protected_text, output)
        for identifier in identifiers:
            self.assertNotIn(identifier, output)


class EmergencyKnowledgeReleaseTests(unittest.TestCase):
    def test_emergency_contacts_are_verified_and_have_no_deployment_placeholder(self) -> None:
        content = (ROOT / "ai_engine/knowledge_base/emergency_contacts.json").read_text(
            encoding="utf-8"
        )
        records = json.loads(content)
        self.assertNotIn("Replace this section", content)
        self.assertGreaterEqual(len(records), 3)
        for record in records:
            with self.subTest(record=record["id"]):
                provenance = record["provenance"]
                self.assertEqual(provenance["verified_on"], "2026-08-05")
                self.assertTrue(provenance["sources"])
                self.assertTrue(all(source["url"].startswith("https://") for source in provenance["sources"]))


if __name__ == "__main__":
    unittest.main()
