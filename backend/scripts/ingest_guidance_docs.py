
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
    logger.info("CTRL4 RAG index build completed.")
    logger.info("Indexed chunks: %s", count)
    logger.info("Documents: %s", rag_service.docs_dir)
    logger.info("Index: %s", rag_service.index_dir)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())