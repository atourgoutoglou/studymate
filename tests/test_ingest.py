import pytest

from app.ingest import split_text


def make_text(number_of_words: int) -> str:
    """Create a test text like 'w0 w1 w2 ...'."""
    return " ".join(f"w{i}" for i in range(number_of_words))


def test_short_text_gives_one_chunk():
    assert split_text("one two three", chunk_size=10, overlap=2) == ["one two three"]


def test_chunks_are_not_bigger_than_chunk_size():
    chunks = split_text(make_text(100), chunk_size=30, overlap=5)
    for chunk in chunks:
        assert len(chunk.split()) <= 30


def test_consecutive_chunks_overlap():
    chunks = split_text(make_text(100), chunk_size=30, overlap=5)
    end_of_first = chunks[0].split()[-5:]
    start_of_second = chunks[1].split()[:5]
    assert end_of_first == start_of_second


def test_no_words_are_lost():
    text = make_text(97)
    chunks = split_text(text, chunk_size=30, overlap=5)
    words_in_chunks = {word for chunk in chunks for word in chunk.split()}
    assert words_in_chunks == set(text.split())


def test_empty_text_gives_no_chunks():
    assert split_text("", chunk_size=10, overlap=2) == []


@pytest.mark.parametrize("chunk_size, overlap", [(0, 0), (10, 10), (10, 50)])
def test_invalid_settings_raise_error(chunk_size, overlap):
    with pytest.raises(ValueError):
        split_text("some text here", chunk_size=chunk_size, overlap=overlap)