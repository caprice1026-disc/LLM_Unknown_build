# LLM_Unknown_build

ゼノフラクタルの残響をコヒーレントに蒸留する、Streamlit製の実験アプリです。

## セットアップ

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## 起動

```bash
streamlit run app.py
```

ブラウザで表示された画面から以下を操作できます。

- 残響生成パラメータ（Seed / フラクタル深度 / 共鳴強度 / 非コヒーレンス）
- 蒸留反復数
- サンプル数

## できること

- 元の残響波形と蒸留後波形の比較
- 周波数ゲート分布の可視化
- Coherence Ratio / Spectral Focus / Phase Stability の確認
- 蒸留結果のSQLite履歴保存（`xeno_resonance.db`）

