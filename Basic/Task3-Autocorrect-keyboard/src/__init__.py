"""Core modules for the Intelligent Autocorrect Keyboard System."""

from .keyboard_engine import KeyboardEngine
from .ngram_model import NGramModel
from .spell_corrector import SpellCorrector

__all__ = ["KeyboardEngine", "NGramModel", "SpellCorrector"]