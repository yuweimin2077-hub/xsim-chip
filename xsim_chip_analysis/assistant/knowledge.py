"""Small auditable BM25 index. Retrieval is lexical, not an embedding model."""

from __future__ import annotations

from collections import Counter
from copy import deepcopy
from importlib.resources import files
import json
import math
import re


ALIASES = {
    "空洞": "solder void", "孔洞": "solder void", "低密度": "low density void",
    "焊桥": "solder bridge", "桥连": "solder bridge", "开路": "copper open",
    "伪影": "artifact threshold", "误报": "false positive", "根因": "cause process evidence",
    "三维": "3d volume", "二维": "2d area", "体积": "volume", "面积": "area",
    "占比": "ratio percentage", "切片": "slice", "重建": "reconstruction",
}


def tokenize(text: str) -> list[str]:
    text = text.lower().replace("_", " ")
    text += " " + " ".join(value for key, value in ALIASES.items() if key in text)
    return re.findall(r"[a-z0-9]+|[\u4e00-\u9fff]", text)


class KnowledgeIndex:
    """Retrieve versioned, attributed cards with English and Chinese summaries."""

    def __init__(self, cards: list[dict] | None = None):
        self.cards = deepcopy(cards) if cards is not None else json.loads(
            files(__package__).joinpath("knowledge.json").read_text(encoding="utf-8")
        )
        ids = [card["id"] for card in self.cards]
        if not ids or len(ids) != len(set(ids)):
            raise ValueError("knowledge IDs must be nonempty and unique")
        self.counts = [Counter(tokenize(" ".join([
            card["title"], card["terms"], card["text"]["en"], card["text"]["zh"],
        ]))) for card in self.cards]
        self.lengths = [sum(count.values()) for count in self.counts]
        self.average_length = sum(self.lengths) / len(self.lengths)
        self.document_frequency = Counter(term for count in self.counts for term in count)

    def search(self, query: str, top_k: int = 4) -> list[dict]:
        if not isinstance(query, str) or not query.strip() or len(query) > 2000:
            raise ValueError("query must contain 1-2000 characters")
        if type(top_k) is not int or not 1 <= top_k <= 7:
            raise ValueError("top_k must be an integer from 1 to 7")
        scores = []
        for card, count, length in zip(self.cards, self.counts, self.lengths):
            score = 0.0
            for term in set(tokenize(query)):
                frequency = count[term]
                if frequency:
                    df = self.document_frequency[term]
                    idf = math.log(1 + (len(self.cards) - df + 0.5) / (df + 0.5))
                    score += idf * frequency * 2.5 / (
                        frequency + 1.5 * (0.25 + 0.75 * length / self.average_length)
                    )
            if score > 0:
                scores.append({**deepcopy(card), "retrieval_score": round(score, 6)})
        return sorted(scores, key=lambda c: (-c["retrieval_score"], c["id"]))[:top_k]
