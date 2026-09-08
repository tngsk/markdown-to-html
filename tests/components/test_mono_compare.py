import sys
import os
import importlib.util

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

spec = importlib.util.spec_from_file_location("mono_compare_parser", "src/components/mono-compare/parser.py")
mono_compare_parser = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mono_compare_parser)
Parser = mono_compare_parser.Parser

def test_compare_parser_modes():
    parser = Parser()

    # 2要素比較のテスト（自動判定で mode="2"）
    md_2 = """@[compare]
:::
### Before
従来の問題点
:::
### After
新しい改善策
@[/compare]"""
    html_2 = parser.process(md_2)
    assert '<mono-compare mode="2"' in html_2
    assert html_2.count('<div class="compare-item"') == 2
    assert "Before" in html_2
    assert "After" in html_2

    # 3要素比較のテスト（自動判定で mode="3"）
    md_3 = """@[compare]
:::
### 制作者視点
設計の意図
:::
### 主成果物
共通の試作品
:::
### 利用者視点
実際の使い勝手
@[end]"""
    html_3 = parser.process(md_3)
    assert '<mono-compare mode="3"' in html_3
    assert html_3.count('<div class="compare-item"') == 3
    assert "制作者視点" in html_3
    assert "主成果物" in html_3
    assert "利用者視点" in html_3


def test_compare_fallback_and_attributes():
    parser = Parser()

    # 明示的な mode 指定の優先および後置属性のテスト
    md = """@[compare](mode: "2"){.custom-border #compare-section}
:::
### 左視点
:::
### 中央視点
:::
### 右視点
@[/compare]"""
    html = parser.process(md)
    assert 'mode="2"' in html
    assert 'class="custom-border"' in html
    assert 'id="compare-section"' in html
    assert html.count('<div class="compare-item"') == 3
