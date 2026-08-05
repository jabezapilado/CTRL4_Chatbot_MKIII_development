
from __future__ import annotations
import logging

from bootstrap import setup_paths

setup_paths()

from server.services import rag_service


logger = logging.getLogger(__name__)


def main() -> int:

    if rag_service.initialization_error:
        logger.error(rag_service.initialization_error)
        return 1

    count = rag_service.build_index()
    report = rag_service.last_build_report
    logger.info("CTRL4 RAG index build completed.")
    logger.info("RAG chunks indexed: %s", count)
    if report:
        logger.info(
            "RAG source summary: discovered=%s indexed=%s skipped=%s fingerprint=%s",
            len(report.discovered_sources),
            len(report.indexed_sources),
            len(report.skipped_sources),
            report.source_fingerprint[:12],
        )
        for skipped in report.skipped_sources:
            logger.warning(
                "RAG source skipped: source=%s reason=%s",
                skipped["source"],
                skipped["reason"],
            )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
