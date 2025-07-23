#!/usr/bin/env python3
"""
Quick test script to verify the example filtering logic works as expected.
"""

import sys
from pathlib import Path

from loguru import logger

# Add the tests directory to the path so we can import from conftest
sys.path.insert(0, str(Path(__file__).parents[2] / "tests" / "template"))

# Import the functions we want to test
from conftest import _discover_examples


def test_filtering() -> None:
    logger.info("Testing example discovery and filtering...")

    # Get all examples
    all_examples = _discover_examples(all_examples=True)
    logger.info(f"All examples found: {[ex.name for ex in all_examples]}")

    # Get filtered examples (latest only)
    filtered_examples = _discover_examples(all_examples=False)
    logger.info(
        f"Filtered examples (latest only): {[ex.name for ex in filtered_examples]}"
    )

    logger.info("Expected behavior:")
    logger.info("- With --all-examples: All examples should be included")
    logger.info(
        "- Without --all-examples: Only 'able_weather_03' should be included (latest in series)"
    )


if __name__ == "__main__":
    test_filtering()
