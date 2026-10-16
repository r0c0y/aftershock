"""EmbeddingGemma (300M, ONNX int8, runs locally on CPU). Used to SUGGEST graph edges, not to answer questions.
Model: onnx-community/embeddinggemma-300m-ONNX (mirror of google/embeddinggemma-300m)."""
import os, numpy as np
import onnxruntime as ort
from tokenizers import Tokenizer

D = os.path.join(os.path.dirname(__file__), "..", "models", "embeddinggemma")
_s = _t = None

def _load():
    global _s, _t
    if _s is None:
        _s = ort.InferenceSession(os.path.join(D, "onnx", "model_quantized.onnx"), providers=["CPUExecutionProvider"])
        _t = Tokenizer.from_file(os.path.join(D, "tokenizer.json")); _t.enable_padding(); _t.enable_truncation(512)
    return _s, _t

def embed(texts, kind="doc"):
    s, t = _load()
    pre = "task: search result | query: " if kind == "query" else "title: none | text: "
    enc = t.encode_batch([pre + x for x in texts])
    ids = np.array([e.ids for e in enc], dtype=np.int64); mask = np.array([e.attention_mask for e in enc], dtype=np.int64)
    feeds = {i.name: v for i, v in zip(s.get_inputs(), [ids, mask]) if i.name in ("input_ids", "attention_mask")}
    out = s.run(None, feeds)
    emb = out[1] if len(out) > 1 else out[0]          # sentence_embedding output
    emb = emb / np.linalg.norm(emb, axis=1, keepdims=True)
    return emb
