# 🚀 Mono 究極のデモケース

ようこそ！このドキュメントは、`Mono` が提供する全機能を駆使して作成されたインタラクティブなデモファイルです。
参加者の皆さんは、このドキュメントを通じて様々な機能をご体験いただけます。

## 1. セッションの開始

まずは、本日のセッションに参加しましょう！

@[session-join: "MONO-MD ワークショップに参加する"]

セッションに参加できたら、ランダムにグループ分けを行ってみましょう。

@[group-assignment: "グループを割り当てる"]

## 2. リアクションとフィードバック

説明中に「わからないな」と思ったり、「なるほど！」と思ったら、いつでもリアクションを送ってください。

@[reaction: "✋ 挙手,💡 なるほど,❓ 質問あり,👏 拍手"]

## 3. インタラクティブなアンケート (Live Polling)

ここまでのセッションはいかがですか？

@[poll: 今日の期待度はどれくらいですか？](非常に高い, 高い, 普通, 少し不安)

## 4. コードブロックとColab変換

Pythonのコード例です。右上の「Copy」ボタンをクリックしてコピーできます。

```python
import asyncio

async def fetch_data():
    print("Fetching data from the universe...")
    await asyncio.sleep(1)
    return {"status": 200, "message": "Success"}

asyncio.run(fetch_data())
```

また、GitHub上のJupyter Notebookリンクは自動的にColabバッジに変換されます！
[データ分析チュートリアルを開く](https://github.com/tngsk/markdown-to-html/blob/main/demo/notebook.ipynb)

## 5. カスタム記法 (Nowrap)

重要なキーワードである {{Mono}} や {{Web Components}} は、画面幅が狭くなっても途中で折り返されず、読みやすさが保たれます。

## 6. 画像の最適化と遅延読み込み (SVG & WebP)

画像はBase64で埋め込まれるか、SVGとして直接インライン化されます。
以下はローカルにあるベクター画像です。

![テスト画像](test.svg)

## 7. A/B テスト (デザイン・音声)

２つのデザインや音声の比較実験を行うことができます。

@[ab-test: デザインの比較](test.svg, test_xml.svg)

## 8. テキストとノートブック入力

学習のメモや、自由記述のアンケートはこちらから入力できます。
リロードしてもデータは保持されます！

**ひとこと感想:**
@[textfield: size:40 (感想をここに入力してください)]

**詳細なノート:**
@[notebook-input](demo-notebook-1)

---
*Created with [Mono]*
