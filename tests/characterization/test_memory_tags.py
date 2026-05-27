# ruff: noqa: ANN001,ANN002,ANN003,ANN201,ANN204,ARG001,ARG002
from src.db.memory.utils import format_tags, merge_tags


def test_format_tags_lowercases_strips_and_concatenates():
    assert format_tags([" Work ", "#Home", "ideas"]) == "#work#home#ideas"


def test_merge_tags_preserves_existing_order_and_adds_missing():
    assert merge_tags("#work#home", ["#HOME", " Health "]) == "#work#home#health"
