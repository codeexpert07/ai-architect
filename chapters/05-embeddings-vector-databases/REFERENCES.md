# Chapter 5 References

This chapter focuses on embeddings, approximate nearest-neighbor search, vector databases, retrieval evaluation, and production retrieval architecture. Prefer primary research and current product documentation for implementation-specific behavior.

## Foundational Research

1. Reimers & Gurevych, **Sentence-BERT: Sentence Embeddings using Siamese BERT-Networks**.
   - https://arxiv.org/abs/1908.10084
2. Karpukhin et al., **Dense Passage Retrieval for Open-Domain Question Answering**.
   - https://arxiv.org/abs/2004.04906
3. Johnson, Douze & Jégou, **Billion-scale similarity search with GPUs** (FAISS).
   - https://arxiv.org/abs/1702.08734
4. Malkov & Yashunin, **Efficient and Robust Approximate Nearest Neighbor Search Using Hierarchical Navigable Small World Graphs**.
   - https://arxiv.org/abs/1603.09320
5. Jégou, Douze & Schmid, **Product Quantization for Nearest Neighbor Search**.
   - https://hal.inria.fr/inria-00514462
6. Nogueira & Cho, **Passage Re-ranking with BERT**.
   - https://arxiv.org/abs/1901.04085
7. Robertson & Zaragoza, **The Probabilistic Relevance Framework: BM25 and Beyond**.
   - https://www.nowpublishers.com/article/Details/INR-019

## Retrieval Evaluation

8. Manning, Raghavan & Schütze, **Introduction to Information Retrieval**.
   - https://nlp.stanford.edu/IR-book/
9. Järvelin & Kekäläinen, **Cumulated gain-based evaluation of IR techniques**.
   - https://doi.org/10.1145/582415.582418

## Current Technology Documentation

- FAISS: https://faiss.ai/
- pgvector: https://github.com/pgvector/pgvector
- Qdrant documentation: https://qdrant.tech/documentation/
- Weaviate documentation: https://docs.weaviate.io/
- Milvus documentation: https://milvus.io/docs/
- Elasticsearch vector search: https://www.elastic.co/guide/en/elasticsearch/reference/current/dense-vector.html
- OpenSearch vector search: https://docs.opensearch.org/latest/vector-search/
- OpenAI embeddings documentation: https://platform.openai.com/docs/guides/embeddings
- Sentence Transformers documentation: https://www.sbert.net/

## Production Engineering

- OpenTelemetry documentation: https://opentelemetry.io/docs/
- NIST AI Risk Management Framework: https://www.nist.gov/itl/ai-risk-management-framework
- OWASP Top 10 for LLM Applications: https://owasp.org/www-project-top-10-for-large-language-model-applications/

## How to Use These References

Use the research papers to understand the algorithms and retrieval principles. Use current database and embedding-provider documentation for exact index parameters, API semantics, limits, filtering behavior, consistency guarantees, and operational procedures. Validate all production choices against representative workload data rather than relying on generic benchmarks.
