"""Run TransformersModel against real torch and transformers with tiny local models.

The checkpoints are randomly initialised and saved to a temporary directory, so no network and no
test double is involved. They exist to prove that the installed torch/transformers release still
accepts the calls in `load_model()` and `predict()` (F020 raised the minimum versions).
`predict()` reports failures as a result with prediction "error", so every test asserts on that.
"""

import pytest

torch = pytest.importorskip("torch")
transformers = pytest.importorskip("transformers")
tokenizers = pytest.importorskip("tokenizers")

from geneforgelang.core.enhanced_inference_engine import (  # noqa: E402
    ModelConfig,
    TransformersModel,
)

SPECIAL_TOKENS = {"unk_token": "[UNK]", "pad_token": "[PAD]", "eos_token": "[EOS]"}
FEATURES = {"experiment_tool": "CRISPR_cas9", "target_gene": "HTT"}


def _save_tiny_tokenizer(path) -> int:
    """Save a word-level tokenizer and return its vocabulary size."""
    words = ["[UNK]", "[PAD]", "[EOS]", "experiment_tool:", "CRISPR_cas9", "target_gene:", "HTT"]
    backend = tokenizers.Tokenizer(
        tokenizers.models.WordLevel({w: i for i, w in enumerate(words)}, unk_token="[UNK]")
    )
    backend.pre_tokenizer = tokenizers.pre_tokenizers.Whitespace()
    transformers.PreTrainedTokenizerFast(tokenizer_object=backend, **SPECIAL_TOKENS).save_pretrained(
        path
    )
    return len(words)


@pytest.fixture
def causal_lm_dir(tmp_path):
    vocab = _save_tiny_tokenizer(tmp_path)
    config = transformers.GPT2Config(
        vocab_size=vocab, n_embd=16, n_layer=1, n_head=2, n_positions=64
    )
    transformers.GPT2LMHeadModel(config).save_pretrained(tmp_path)
    return tmp_path


@pytest.fixture
def classifier_dir(tmp_path):
    vocab = _save_tiny_tokenizer(tmp_path)
    config = transformers.BertConfig(
        vocab_size=vocab,
        hidden_size=16,
        num_hidden_layers=1,
        num_attention_heads=2,
        intermediate_size=32,
        num_labels=2,
    )
    transformers.BertForSequenceClassification(config).save_pretrained(tmp_path)
    return tmp_path


@pytest.mark.parametrize(
    ("model_type", "fixture_name"),
    [("causal_lm", "causal_lm_dir"), ("sequence_classification", "classifier_dir")],
)
def test_load_and_predict_with_installed_transformers(model_type, fixture_name, request):
    model_dir = request.getfixturevalue(fixture_name)
    model = TransformersModel(ModelConfig(model_name=str(model_dir), model_type=model_type))

    model.load_model()
    result = model.predict(FEATURES)

    assert model.is_loaded()
    assert result.prediction != "error", result.explanation
    assert 0.0 < result.confidence <= 1.0
