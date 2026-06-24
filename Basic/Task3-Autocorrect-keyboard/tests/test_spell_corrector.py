from src.spell_corrector import SpellCorrector


def test_misspelled_detection_and_correction() -> None:
    corrector = SpellCorrector()
    text = "I am goinng to the markket"

    misspelled = corrector.find_misspelled_words(text)

    assert "goinng" in misspelled
    assert "markket" in misspelled
    assert misspelled["goinng"] == "going"

    corrected = corrector.correct_sentence(text).lower()
    assert corrected == "i am going to the market"