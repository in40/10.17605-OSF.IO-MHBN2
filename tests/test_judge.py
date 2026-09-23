from smoke_judge.runner import parse_scores


def test_parse_combined_plain():
    s = '{"faithfulness": 0.9, "coverage": 0.7, "coherence": 0.8, "fluency": 0.95}'
    out = parse_scores(s, "combined")
    assert out == {"faithfulness": 0.9, "coverage": 0.7, "coherence": 0.8, "fluency": 0.95}


def test_parse_combined_with_fences():
    s = '```json\n{"faithfulness": 1, "coverage": 0.5, "coherence": 0.6, "fluency": 0.7}\n```'
    out = parse_scores(s, "combined")
    assert out is not None and out["coverage"] == 0.5


def test_parse_combined_missing_dim():
    s = '{"faithfulness": 0.9}'
    assert parse_scores(s, "combined") is None


def test_parse_per_dim():
    s = 'answer: {"score": 0.8}'
    out = parse_scores(s, "per_dimension")
    assert out == {"score": 0.8}


def test_parse_no_json():
    assert parse_scores("no json here", "combined") is None
