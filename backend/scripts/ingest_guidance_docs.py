from __future__ import annotations

from bootstrap import setup_paths

setup_paths()

from server.services import rag_service


def main() -> int:

    if rag_service.initialization_error:
        print(rag_service.initialization_error)
        return 1

    count = rag_service.build_index()

    print("=" * 60)
    print("CTRL4 RAG INDEX BUILDER")
    print("=" * 60)
    print(f"Indexed chunks : {count}")
    print(f"Documents      : {rag_service.docs_dir}")
    print(f"Index          : {rag_service.index_dir}")
    print("=" * 60)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())