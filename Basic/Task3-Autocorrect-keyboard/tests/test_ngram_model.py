from src.ngram_model import NGramModel


def test_predict_next_words_returns_list() -> None:
    corpus = """
    i am going to the market
    i am going to the office
    i am going to the school
    """
    model = NGramModel()
    model.train(corpus)

    predictions = model.predict_next_words("i am going to the", top_k=3)

    assert isinstance(predictions, list)
    assert len(predictions) > 0
    assert "market" in predictions or "office" in predictions or "school" in predictions