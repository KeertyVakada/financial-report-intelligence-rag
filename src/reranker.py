from sentence_transformers import CrossEncoder


MODEL_NAME = "cross-encoder/ms-marco-MiniLM-L-6-v2"

model = CrossEncoder(MODEL_NAME)


def rerank(
    query: str,
    candidates: list[dict],
    top_k: int = 5
) -> list[dict]:

    if not query.strip():
        raise ValueError("Query cannot be empty.")

    if not candidates:
        return []

    # ---------------------------------------------------------
    # Cross-encoder relevance scoring
    # ---------------------------------------------------------

    pairs = [
        (query, candidate["text"])
        for candidate in candidates
    ]

    scores = model.predict(pairs)

    scored_candidates = []

    for candidate, score in zip(candidates, scores):

        candidate_copy = candidate.copy()

        candidate_copy["reranker_score"] = float(score)

        scored_candidates.append(candidate_copy)

    # ---------------------------------------------------------
    # Normalize cross-encoder score
    # ---------------------------------------------------------

    reranker_scores = [
        candidate["reranker_score"]
        for candidate in scored_candidates
    ]

    min_score = min(reranker_scores)
    max_score = max(reranker_scores)

    if max_score == min_score:

        for candidate in scored_candidates:
            candidate["reranker_normalized"] = 0.0

    else:

        for candidate in scored_candidates:

            candidate["reranker_normalized"] = (
                candidate["reranker_score"] - min_score
            ) / (
                max_score - min_score
            )

    # ---------------------------------------------------------
    # Financial-aware final score
    # ---------------------------------------------------------

    query_lower = query.lower()

    for candidate in scored_candidates:

        financial_score = candidate.get(
            "financial_score",
            0.0
        )

        evidence_score = candidate.get(
            "evidence_score",
            0.0
        )

        reranker_score = candidate.get(
            "reranker_normalized",
            0.0
        )

        evidence_type = candidate.get(
            "evidence_type",
            ""
        )

        final_score = reranker_score

        # -----------------------------------------------------
        # Segment questions
        # -----------------------------------------------------

        if any(
            term in query_lower
            for term in [
                "segment",
                "productivity and business processes",
                "intelligent cloud",
                "more personal computing"
            ]
        ):

            if evidence_type == "segment_table":
                final_score += 0.40

            elif evidence_type == "financial_table":
                final_score += 0.15

            elif evidence_type == "financial_statement":
                final_score += 0.10

            elif evidence_type == "narrative":
                final_score += 0.02

        # -----------------------------------------------------
        # Product / service revenue questions
        # -----------------------------------------------------

        elif any(
            term in query_lower
            for term in [
                "gaming",
                "server",
                "linkedin",
                "microsoft 365",
                "dynamics",
                "windows",
                "search",
                "product",
                "service"
            ]
        ):

            if evidence_type == "revenue_table":
                final_score += 0.35

            elif evidence_type == "financial_table":
                final_score += 0.15

        # -----------------------------------------------------
        # General financial questions
        # -----------------------------------------------------

        final_score += financial_score * 0.50
        final_score += evidence_score * 0.50

        candidate["final_ranking_score"] = final_score

    # ---------------------------------------------------------
    # Final ranking
    # ---------------------------------------------------------

    scored_candidates.sort(
        key=lambda x: x["final_ranking_score"],
        reverse=True
    )

    # ---------------------------------------------------------
    # Assign final ranks
    # ---------------------------------------------------------

    results = scored_candidates[:top_k]

    for rank, candidate in enumerate(results, start=1):

        candidate["reranker_rank"] = rank

    return results