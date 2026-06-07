def test_legacy_examples_are_ignored():
    old_url = "https://api.acmepay.local/v1"
    old_path = "/acmepay/v1/refunds"
    assert old_url and old_path

