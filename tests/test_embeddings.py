import numpy as np

from app.embeddings import load_cache, save_cache, text_key


def test_same_text_gives_same_key():
    assert text_key("hello world") == text_key("hello world")


def test_different_texts_give_different_keys():
    assert text_key("hello world") != text_key("hello there")


def test_cache_is_saved_and_loaded(tmp_path):
    cache_file = tmp_path / "embeddings.npz"
    cache = {text_key("a"): np.array([1.0, 2.0]), text_key("b"): np.array([3.0, 4.0])}

    save_cache(cache, cache_file)
    loaded = load_cache(cache_file)

    assert set(loaded) == set(cache)
    assert np.allclose(loaded[text_key("b")], [3.0, 4.0])


def test_missing_cache_file_gives_empty_cache(tmp_path):
    assert load_cache(tmp_path / "does_not_exist.npz") == {}