import streamlit as st

from financial_evidence_retrieval import retrieve_financial_evidence
from reranker import rerank
from context_builder import build_context
from generation import generate_answer


# =========================================================
# Page configuration
# =========================================================

st.set_page_config(
    page_title="Financial Report Intelligence Assistant",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed",
)


# =========================================================
# Custom styling
# =========================================================

st.markdown(
    """
    <style>

    /* Main container */
    .block-container {
        max-width: 1200px;
        padding-top: 2rem;
        padding-bottom: 3rem;
    }

    /* Header */
    .main-title {
        font-size: 2.6rem;
        font-weight: 700;
        margin-bottom: 0.25rem;
    }

    .subtitle {
        font-size: 1.05rem;
        color: #9ca3af;
        margin-bottom: 1.5rem;
    }

    /* Answer card */
    .answer-card {
        padding: 1.4rem 1.5rem;
        border-radius: 12px;
        border: 1px solid rgba(128, 128, 128, 0.25);
        background: rgba(128, 128, 128, 0.06);
        margin-top: 0.5rem;
        margin-bottom: 1rem;
    }

    .answer-label {
        font-size: 0.85rem;
        font-weight: 600;
        color: #9ca3af;
        margin-bottom: 0.5rem;
        text-transform: uppercase;
        letter-spacing: 0.04em;
    }

    /* Source information */
    .source-card {
        padding: 0.9rem 1rem;
        border-radius: 10px;
        border: 1px solid rgba(128, 128, 128, 0.20);
        margin-top: 0.8rem;
    }

    .source-title {
        font-weight: 600;
        margin-bottom: 0.35rem;
    }

    .source-meta {
        color: #9ca3af;
        font-size: 0.9rem;
    }

    /* Evidence heading */
    .evidence-description {
        color: #9ca3af;
        margin-top: -0.4rem;
        margin-bottom: 1rem;
    }

    /* Technical details */
    .technical-note {
        color: #9ca3af;
        font-size: 0.85rem;
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# Header
# =========================================================

st.markdown(
    '<div class="main-title">📊 Financial Report Intelligence Assistant</div>',
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="subtitle">
    Ask natural-language questions about Microsoft's 2025 Annual Report
    and receive answers grounded in the report's retrieved evidence.
    </div>
    """,
    unsafe_allow_html=True,
)

st.divider()


# =========================================================
# Question input
# =========================================================

question = st.text_input(
    "Ask a question",
    placeholder="Example: What was Microsoft's revenue in fiscal year 2025?",
)


# =========================================================
# Example questions
# =========================================================

with st.expander("💡 Example questions"):

    example_questions = [
        "What was Microsoft's revenue in fiscal year 2025?",
        "Which business segment had the highest revenue in 2025?",
        "What was Gaming revenue in 2025?",
        "What was Microsoft's net income in 2025?",
        "What was Microsoft's operating income in 2025?",
        "How much cash did Microsoft generate from operations?",
    ]

    for example in example_questions:
        st.markdown(f"• {example}")


# =========================================================
# Run RAG pipeline
# =========================================================

if question.strip():

    with st.spinner("Analyzing the financial report..."):

        try:

            # -------------------------------------------------
            # Step 1: Retrieve financial evidence
            # -------------------------------------------------

            retrieved_candidates = retrieve_financial_evidence(
                query=question,
                top_k=20,
            )

            if not retrieved_candidates:

                st.warning(
                    "I couldn't find relevant evidence in the "
                    "Microsoft 2025 Annual Report."
                )

                st.stop()


            # -------------------------------------------------
            # Step 2: Rerank retrieved candidates
            # -------------------------------------------------

            reranked_chunks = rerank(
                query=question,
                candidates=retrieved_candidates,
                top_k=5,
            )

            if not reranked_chunks:

                st.warning(
                    "No sufficiently relevant evidence was found "
                    "for this question."
                )

                st.stop()


            # -------------------------------------------------
            # Step 3: Build grounded context
            # -------------------------------------------------

            context = build_context(
                retrieved_chunks=reranked_chunks,
                max_chunks=5,
            )


            # -------------------------------------------------
            # Step 4: Generate answer
            # -------------------------------------------------

            answer = generate_answer(
                question=question,
                context=context,
            )


        except Exception as e:

            st.error(
                "Something went wrong while processing your question."
            )

            st.exception(e)

            st.stop()


    # =========================================================
    # Answer section
    # =========================================================

    st.subheader("💬 Answer")

    st.markdown(
        f"""
        <div class="answer-card">

        <div class="answer-label">Grounded answer</div>

        {answer}

        </div>
        """,
        unsafe_allow_html=True,
    )


    # =========================================================
    # Primary source
    # =========================================================

    primary_chunk = reranked_chunks[0]

    primary_source = primary_chunk.get(
        "document",
        "Microsoft 2025 Annual Report",
    )

    primary_report_page = primary_chunk.get(
        "report_page",
        "N/A",
    )

    primary_pdf_page = primary_chunk.get(
        "pdf_page",
        "N/A",
    )

    primary_evidence_type = primary_chunk.get(
        "evidence_type",
        "General evidence",
    )

    st.markdown(
        f"""
        <div class="source-card">

        <div class="source-title">
        📄 Primary source
        </div>

        <div>
        {primary_source}
        </div>

        <div class="source-meta">
        Report page {primary_report_page}
        &nbsp;·&nbsp;
        PDF page {primary_pdf_page}
        &nbsp;·&nbsp;
        {primary_evidence_type.replace("_", " ").title()}
        </div>

        </div>
        """,
        unsafe_allow_html=True,
    )


    # =========================================================
    # Supporting evidence
    # =========================================================

    st.divider()

    st.subheader("📚 Supporting Evidence")

    st.markdown(
        """
        <div class="evidence-description">
        Evidence retrieved from the Microsoft 2025 Annual Report
        and used to support the answer.
        </div>
        """,
        unsafe_allow_html=True,
    )


    for i, chunk in enumerate(
        reranked_chunks,
        start=1,
    ):

        # -----------------------------------------------------
        # Metadata
        # -----------------------------------------------------

        source = chunk.get(
            "document",
            "Microsoft 2025 Annual Report",
        )

        pdf_page = chunk.get(
            "pdf_page",
            "N/A",
        )

        report_page = chunk.get(
            "report_page",
            "N/A",
        )

        evidence_type = chunk.get(
            "evidence_type",
            "general",
        )

        evidence_type_display = (
            evidence_type
            .replace("_", " ")
            .title()
        )

        text = chunk.get(
            "text",
            "",
        ).strip()


        # -----------------------------------------------------
        # Evidence expander
        # -----------------------------------------------------

        with st.expander(
            f"Evidence {i}  ·  {evidence_type_display}"
        ):

            # Source
            st.markdown(
                f"**📄 Source:** {source}"
            )

            # Page information
            col1, col2 = st.columns(2)

            with col1:

                st.markdown(
                    f"**Report page:** {report_page}"
                )

            with col2:

                st.markdown(
                    f"**PDF page:** {pdf_page}"
                )


            # Evidence type
            st.markdown(
                f"**Evidence type:** {evidence_type_display}"
            )


            # Evidence text
            st.markdown("**Supporting text**")

            st.text_area(
                label=f"Evidence text {i}",
                value=text,
                height=220,
                disabled=True,
                label_visibility="collapsed",
            )

    # =========================================================
    # Retrieval pipeline information
    # =========================================================

    st.divider()

    with st.expander("⚙️ How this answer was generated"):

        st.markdown(
            """
            **1. Hybrid retrieval**  
            Dense semantic retrieval + BM25 lexical retrieval.

            **2. Financial-aware ranking**  
            Retrieved passages are scored using financial
            concepts such as revenue, assets, cash flow,
            segments, and financial statements.

            **3. Evidence-aware ranking**  
            Evidence is classified by type, such as financial
            statements, revenue tables, segment tables, and
            cash-flow tables.

            **4. Reranking**  
            A cross-encoder reranks the strongest retrieved
            candidates.

            **5. Grounded generation**  
            The LLM generates an answer using the retrieved
            report evidence rather than relying only on
            general model knowledge.
            """
        )


# =========================================================
# Footer
# =========================================================

st.divider()

st.caption(
    "Financial Report Intelligence Assistant • "
    "Hybrid Retrieval • Financial-Aware Evidence Ranking • "
    "Grounded Generation"
)