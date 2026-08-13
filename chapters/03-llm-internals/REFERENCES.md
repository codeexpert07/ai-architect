# Chapter 3 References

This chapter emphasizes primary and foundational sources. Vendor documentation should be consulted for current model-specific behavior because model architectures, serving APIs, context limits, and inference optimizations evolve rapidly.

## Foundational Papers

1. Vaswani et al., **Attention Is All You Need** — introduces the Transformer architecture.
   - https://arxiv.org/abs/1706.03762
2. Devlin et al., **BERT: Pre-training of Deep Bidirectional Transformers for Language Understanding** — important encoder-only Transformer reference.
   - https://arxiv.org/abs/1810.04805
3. Brown et al., **Language Models are Few-Shot Learners** — influential large-language-model scaling and in-context learning work.
   - https://arxiv.org/abs/2005.14165
4. Kaplan et al., **Scaling Laws for Neural Language Models** — useful background for thinking about model/data/compute scaling.
   - https://arxiv.org/abs/2001.08361
5. Hoffmann et al., **Training Compute-Optimal Large Language Models** — important discussion of model/data scaling trade-offs.
   - https://arxiv.org/abs/2203.15556
6. Shazeer, **Fast Transformer Decoding: One Write-Head is All You Need** — background for multi-query attention and inference efficiency.
   - https://arxiv.org/abs/1911.02150
7. Ainslie et al., **GQA: Training Generalized Multi-Query Transformer Models from Multi-Head Checkpoints** — grouped-query attention.
   - https://arxiv.org/abs/2305.13245
8. Dettmers et al., **LLM.int8(): 8-bit Matrix Multiplication for Transformers at Scale** — quantization background.
   - https://arxiv.org/abs/2208.07339
9. Frantar et al., **GPTQ: Accurate Post-Training Quantization for Generative Pre-trained Transformers** — post-training quantization.
   - https://arxiv.org/abs/2210.17323
10. Kwon et al., **Efficient Memory Management for Large Language Model Serving with PagedAttention** — foundation for modern KV-cache-aware serving approaches.
    - https://arxiv.org/abs/2309.06180

## Serving and Inference

- vLLM documentation: https://docs.vllm.ai/
- NVIDIA TensorRT-LLM documentation: https://nvidia.github.io/TensorRT-LLM/
- Hugging Face Text Generation Inference: https://huggingface.co/docs/text-generation-inference/
- Hugging Face Transformers documentation: https://huggingface.co/docs/transformers/

## Architecture and Risk

- NIST AI Risk Management Framework: https://www.nist.gov/itl/ai-risk-management-framework
- Stanford CRFM: https://crfm.stanford.edu/

## How to Use These References

For this handbook, prioritize the original paper when learning an architectural concept and current serving documentation when implementing it. Do not assume that a technique described in an older paper is exposed identically by a current model provider.
