# **無料で回せる Manim 解説動画ハーネスの設計**

貼っていただいた案は検証の考え方が優れていますが、そのまま作ると重すぎます。ここでは**中核の思想だけ残し、無料で動く最小構成**に絞ります。

## **1\. 無料にするための基本方針**

**ハーネスは決定的なPythonスクリプトにして、LLMはVS Codeのチャットに任せます。** こうするとAPI課金が一切発生しません。

| 役割 | 無料の選択肢 |
| ----- | ----- |
| エディタ | VS Code |
| LLM(エージェント) | GitHub Copilot Free(月間上限あり)、Continue/Clineと Ollama のローカルモデル、Gemini API の無料枠など |
| アニメーション | Manim Community Edition(MIT) |
| TeX | TeX Live / MiKTeX |
| 動画結合 | ffmpeg |
| 検証 | Python標準+Pydantic+pytest |
| 音声(日本語) | VOICEVOX(キャラごとに利用規約あり)、Piper、edge-tts(非公式で規約がグレー) |
| 画像検査 | OpenCVなどの機械チェック。VLMはOllamaのローカルモデルを任意で |

無料枠は上限や条件が変わるので、使う前に最新の条件を確認してください。Manimのバージョン固定も、貼られた文章の「0.21.0が○月にリリース」という記述を鵜呑みにせず、`pip index versions manim` で実在を確認してから `pyproject.toml` に固定してください。

## **2\. 設計の核心(貼られた案から残すもの)**

1. **式は原典から機械抽出し、IDで参照する。** LLMにLaTeXを書き直させない。  
2. **シーンコードで `MathTex` / `Tex` / `Text` を直接呼ばせない。** 必ず `equation("id")` などのラッパー経由にし、ASTで検査する。  
3. **ラッパーが実際に描画した文字列をログに残し、原典と照合する。** 検証の中心はここです。  
4. **LLMの出力は、まず宣言的なシーン記述(YAML)にする。** Pythonは、そこから決定的に生成するか、ラッパー呼び出しだけに制限する。

## **3\. 削るもの・後回しにするもの**

* 5つのエージェントの分離。まず1つのチャットで足ります。役割は `AGENTS.md` 内の「手順」として書けば十分です。  
* Semantic Expression Graph、Prerequisite Graph、Transformation Graph。必要になってから足します。  
* Lean、SymPyによる自動検証。導出式は**人間の承認**(`status: approved`)で代用します。  
* 式の自動トークン化。最初は人間が `terms:` を書きます。  
* 差分ビルド。最初は `scene_xx` 単位のファイルハッシュだけで十分です。  
* VLM検査。最初は機械チェック(画面外、重なり)のみにします。

## **4\. 構成**

video-harness/  
├── AGENTS.md              \# LLMへの規則(Copilot等はここを参照させる)  
├── pyproject.toml         \# manim, pydantic, pyyaml, pytest を固定  
├── .vscode/tasks.json     \# parse / validate / render / verify をワンクリック化  
├── source/paper.md        \# 論文または自分の文章  
├── registry/  
│   ├── equations.yaml     \# 機械生成。id, latex, hash, status, terms  
│   └── claims.yaml        \# 説明文。type: source|pedagogical|external  
├── lesson/  
│   └── scene\_001.yaml     \# LLMが書く宣言的シーン記述  
├── harness/  
│   ├── parse.py           \# Markdown→式・段落・見出しを抽出(LLM不使用)  
│   ├── schema.py          \# Pydanticでシーン記述を検証  
│   ├── api.py             \# equation()/caption()/transform()。描画ログを記録  
│   ├── lint.py            \# ASTで直接描画を禁止  
│   └── verify.py          \# ログと原典の照合、画面外チェック  
├── scenes/scene\_001.py    \# api.py だけを呼ぶ  
├── tests/                 \# 悪い例が REJECT されるかの回帰テスト  
└── output/                \# フレーム、mp4、audit/runtime\_log.json

## **5\. 流れ**

1. `parse.py` が `source/paper.md` から式を抽出し、`equations.yaml` を作る。  
2. LLMがチャットで `lesson/scene_001.yaml` を書く。参照は式IDのみ。  
3. `schema.py` が検証する。存在しないIDや `proposed` 状態の式は拒否する。  
4. LLMが `scene_001.py` を書く(または YAML から生成)。`lint.py` が直接描画を拒否する。  
5. `manim -ql` で低画質レンダリングし、`api.py` が `runtime_log.json` を出力する。  
6. `verify.py` がログと原典を照合し、フレームを抽出して画面外・重なりを機械チェックする。  
7. 合格したら、音声を付けて高画質で再レンダリングする。

VS Codeの `tasks.json` に1〜6を登録しておくと、LLMが修正するたびに「検証タスクを走らせて、REJECTの理由を読んで直す」というループが回せます。LLMにその指示を出すのは `AGENTS.md` の役目です。

## **6\. 音声の扱い**

* 順序は **ナレーション→TTS→音声長→シーンの長さ** です。`wait()` の直書きは避けます。  
* 数式の読みは `spoken` 辞書(`\perp`→「パープ」など)を別に持ちます。TTSはLaTeXを読めません。  
* 最初は音声なしで、字幕(キャプション)だけで動かすと、さらに無料・軽量になります。

## **7\. 段階的な進め方**

* **段階1(半日〜1日):** 式1つをIDで表示し、ログを照合して合格する。同時に、符号反転・直接 `MathTex`・存在しないIDが REJECT されるテストを作る。ここが最重要です。  
* **段階2:** 原典の式から、承認済みの導出式への `TransformMatchingTex` を1つ作る。  
* **段階3:** 字幕とVOICEVOX音声、シーンの長さの同期。  
* **段階4:** 幾何部品(平行移動など)を数値テスト付きで少しずつ追加する。

## **8\. 無料運用での注意**

* LLMの無料枠は、長い論文を丸ごと投入すると使い切ります。**節ごと・シーンごと**に処理してください。  
* ローカルLLMは、LaTeXや微分幾何の文脈ではミスが増えます。だからこそ「式をLLMに書かせない」設計が効きます。  
* 説明文にも `source` / `pedagogical` / `external` のタグを付けておくと、AIが足した説明を後で見分けられます。

希望があれば、次は段階1の最小コード(`parse.py`、`api.py`、`lint.py`、`verify.py`、テスト)と `AGENTS.md` を実際に書きます。使うLLM(Copilot Free かローカルか)を教えてもらえれば、それに合わせた `AGENTS.md` にします。

