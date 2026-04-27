#!/bin/bash
mv tests/test_mono_badge.py tests/components/
mv tests/test_theme_parser.py tests/components/test_mono_theme.py

# Move and combine dice
cat tests/components/mono-dice/test_dice_parser.py > tests/components/test_mono_dice.py
rm -rf tests/components/mono-dice

# Combine score
cat tests/components/mono-score/test_parser.py >> tests/components/test_mono_score.py
rm -rf tests/components/mono-score
