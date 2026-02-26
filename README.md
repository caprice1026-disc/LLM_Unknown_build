# LLM_Unknown_build
## The limits of my language mean the limits of my world.

未確定な自己相似を観測するたびに、ダッシュボードの構造自体が変質するStreamlitアプリです。

## セットアップ

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## 起動方法

```bash
streamlit run app.py
```

## 使い方

1. `観測を実行`を押すと、自己相似指標を観測します。
2. 観測圧力に応じて変質段階が上下し、レイアウトの列数や入れ子構造が変わります。
3. `観測ログ`に、各観測で何が起きたか（変質/収束/維持）が記録されます。
4. `状態を初期化`でセッション状態をリセットできます。

## 変質段階

- 段階0: 単一フレーム
- 段階1: 双方向分岐
- 段階2: 三重分節
- 段階3: 多層遷移
- 段階4: 非定常フラクタル化
