"""RAG Worker: Hybrid retrieval over incident runbooks."""

from __future__ import annotations
import re
from pathlib import Path
from typing import Any
from unittest import result

import chromadb
from rank_bm25 import BM25Okapi



# TODO: Milestone 2: Implement ChromaDB + BM25Okapi + RRF

class RagWorker:
    """Combines ChromaDB dense vector search with BM25 sparse lexical search
    using Reciprocal Rank Fusion (RRF) to retrieve the best runbook for an incident."""
    def __init__(self, runbooks_dir: Path | str | None = None) -> None:
        if runbooks_dir is None:
            self.runbooks_dir = (Path(__file__).resolve().parent.parent.parent
                                 /"data"
                                 / "runbooks")
        else:
            self.runbooks_dir = Path(runbooks_dir)

        self.doc_ids: list[str] = []
        self.doc_texts: list[str] = []
        self.doc_map: dict[str, str] = {}

        # Initialize In-Memory ChromaDB
        self.chroma_client = chromadb.EphemeralClient()
        self.collection = self.chroma_client.get_or_create_collection(
            name="sentinel_runbooks"
        )

        # Ingest markdown runbooks into both indexes
        self._load_and_index_runbooks()

    def _tokenize(self, text: str) -> list[str]:
        """Tokenize a text into a list of tokens."""
        return re.findall(r"\w+", text.lower())

    def _load_and_index_runbooks(self) -> None:
        """Reads all .md files in the runbooks folder and builds Dense & Sparse indexes."""
        md_files = list(self.runbooks_dir.glob("*.md"))
        if not md_files:
            print(f"No .md files found in runbooks {self.runbooks_dir} folder.")
            return
        for md_file in md_files:
            content = md_file.read_text(encoding="utf-8")
            doc_id = md_file.stem

            self.doc_ids.append(doc_id)
            self.doc_texts.append(content)
            self.doc_map[doc_id] = content

            # Index into chromaDB
            self.collection.add(
                ids=self.doc_ids,
                documents=self.doc_texts,
                metadatas=[{"filename": f"{doc_id}.md"} for doc_id in self.doc_ids],
            )

            # Index into BM25 (Sparse)
            tokenized_corpus = [self._tokenize(text) for text in self.doc_texts]
            self.bm25 = BM25Okapi(tokenized_corpus)

    def search_dense(self, query: str, top_k: int = 4) -> list[str]:
        """Retrieves document IDs ranked by ChromaDB semantic similarity."""
        results = self.collection.query(
            query_texts=[query], n_results= min(top_k, len(self.doc_ids))
        )
        return results["ids"][0] if results["ids"] else []
    def search_sparse(self, query: str, top_k: int = 4) -> list[str]:
        """Retrieves document IDs ranked by ChromaDB semantic similarity."""
        query_tokens = self._tokenize(query)
        scores = self.bm25.get_scores(query_tokens)

        ranked_docs = sorted(
            zip(self.doc_ids, scores),key=lambda x: x[1], reverse=True
        )
        return [doc_id for doc_id, score in ranked_docs[:top_k]]

    def retrieve(self, query: str, top_k: int = 1, rrf_k: int = 60) -> list[dict[str, Any]]:
        """Performs Reciprocal Rank Fusion (RRF) between Dense and Sparse search.
        RRF Formula:
            score(d) = 1 / (rrf_k + dense_rank) + 1 / (rrf_k + sparse_rank)"""
        dense_ranked_ids = self.search_dense(query, top_k=len(self.doc_ids))
        sparse_ranked_ids = self.search_sparse(query, top_k=len(self.doc_ids))

        # Map doc_id to its 1-based rank position
        dense_rank_map = {
            doc_id: rank
            for rank, doc_id in enumerate(dense_ranked_ids, start=1)
        }
        sparse_rank_map = {
            doc_id: rank
            for rank, doc_id in enumerate(sparse_ranked_ids, start=1)
        }

        rrf_scores: dict[str, float] = {}
        for doc_id in self.doc_ids:
            score = 0.0
            if doc_id in dense_rank_map:
                score += 1.0 / (rrf_k + dense_rank_map[doc_id])
            if doc_id in sparse_rank_map:
                score += 1.0 / (rrf_k + sparse_rank_map[doc_id])
            rrf_scores[doc_id] = score

        sorted_ids = sorted(
            rrf_scores.keys(), key=lambda x: rrf_scores[x], reverse=True
        )

        results = []
        for doc_id in sorted_ids[:top_k]:
            results.append(
                {
                    "doc_id": doc_id,
                    "content": self.doc_map[doc_id],
                    "rrf_score": rrf_scores[doc_id],
                    "dense_rank": dense_rank_map.get(doc_id),
                    "sparse_rank": sparse_rank_map.get(doc_id),
                }
            )
        return results


