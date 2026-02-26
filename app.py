"""未確定な自己相似を観測するたびに構造が変質するStreamlitダッシュボード。"""

from __future__ import annotations

import math
import random
from datetime import datetime

import streamlit as st

MAX_STAGE = 4



def initialize_state() -> None:
    """セッション状態を初期化する。"""
    defaults = {
        "observations": 0,
        "stage": 0,
        "resonance": 0.35,
        "history": [],
        "seed": random.randint(1, 10_000),
    }
    for key, value in defaults.items():
        st.session_state.setdefault(key, value)



def observe_uncertain_self_similarity() -> dict[str, float | str | int]:
    """未確定な自己相似を観測し、指標群を返す。"""
    step = st.session_state.observations + 1
    phase = step / 2.4
    drift = random.uniform(-0.14, 0.14)
    raw_similarity = 0.5 + 0.32 * math.sin(phase + st.session_state.seed / 3000) + drift
    similarity = max(0.02, min(0.98, raw_similarity))

    ambiguity = abs(0.5 - similarity) * 2
    mutation_pressure = (1 - ambiguity) * random.uniform(0.68, 1.28)
    coherence = (similarity * 0.6) + ((1 - ambiguity) * 0.4)

    return {
        "timestamp": datetime.now().strftime("%H:%M:%S"),
        "step": step,
        "similarity": similarity,
        "ambiguity": ambiguity,
        "pressure": mutation_pressure,
        "coherence": coherence,
    }



def apply_mutation(observation: dict[str, float | str | int]) -> str:
    """観測結果を適用し、必要に応じて構造段階を更新する。"""
    pressure = float(observation["pressure"])
    coherence = float(observation["coherence"])

    st.session_state.observations = int(observation["step"])
    st.session_state.resonance = (st.session_state.resonance * 0.58) + (coherence * 0.42)

    event = "位相は揺らいだが、構造は維持された"
    if pressure > 0.64 and st.session_state.stage < MAX_STAGE:
        st.session_state.stage += 1
        event = f"変質が発生: 段階 {st.session_state.stage} へ遷移"
    elif pressure < 0.26 and st.session_state.stage > 0:
        st.session_state.stage -= 1
        event = f"収束が発生: 段階 {st.session_state.stage} へ回帰"

    st.session_state.history.insert(
        0,
        {
            **observation,
            "event": event,
            "stage": st.session_state.stage,
            "resonance": st.session_state.resonance,
        },
    )

    st.session_state.history = st.session_state.history[:18]
    return event



def render_cells(columns_count: int, title_prefix: str, depth: int) -> None:
    """段階表現用のセルを描画する。"""
    columns = st.columns(columns_count)
    for idx, col in enumerate(columns, start=1):
        frag = (st.session_state.resonance + idx / (columns_count + depth + 1)) % 1
        density = abs(math.sin((st.session_state.observations + idx + depth) / 3.2))
        col.metric(f"{title_prefix}{idx}", f"{frag:.3f}", delta=f"密度 {density:.2f}")



def render_structure(stage: int) -> None:
    """現在段階に応じて構造を描画する。"""
    st.subheader("構造変質ビュー")

    if stage == 0:
        st.info("段階0: 原初セル。単一フレームで自己相似を観測中。")
        render_cells(columns_count=1, title_prefix="セル", depth=0)
        return

    if stage == 1:
        st.warning("段階1: 双方向分岐。観測に応じて左右対称が崩れ始める。")
        render_cells(columns_count=2, title_prefix="分岐", depth=1)
        return

    if stage == 2:
        st.success("段階2: 三重分節。構造が局所クラスタへ分化。")
        render_cells(columns_count=3, title_prefix="節", depth=2)
        st.progress(min(1.0, st.session_state.resonance), text="共鳴率")
        return

    if stage == 3:
        st.error("段階3: 多層遷移。観測点ごとに異なる位相層が発生。")
        render_cells(columns_count=4, title_prefix="層", depth=3)
        with st.container(border=True):
            st.caption("副次構造")
            render_cells(columns_count=2, title_prefix="副層", depth=4)
        return

    st.markdown("### 段階4: 非定常フラクタル化")
    primary, secondary = st.columns((2, 1))
    with primary:
        render_cells(columns_count=5, title_prefix="主枝", depth=4)
    with secondary:
        st.metric("共鳴核", f"{st.session_state.resonance:.3f}")
        st.metric("観測回数", f"{st.session_state.observations}")
        st.metric("変質段階", f"{st.session_state.stage}")

    with st.container(border=True):
        st.caption("入れ子自己相似")
        nested_a, nested_b = st.columns(2)
        with nested_a:
            render_cells(columns_count=2, title_prefix="内枝A-", depth=5)
        with nested_b:
            render_cells(columns_count=2, title_prefix="内枝B-", depth=6)



def render_history() -> None:
    """観測履歴を表示する。"""
    st.subheader("観測ログ")
    if not st.session_state.history:
        st.write("まだ観測は行われていません。")
        return

    for item in st.session_state.history[:8]:
        st.markdown(
            (
                f"- `{item['timestamp']}` # {item['step']} / 類似度 `{item['similarity']:.3f}` "
                f"/ 曖昧度 `{item['ambiguity']:.3f}` / 圧力 `{item['pressure']:.3f}` "
                f"/ 段階 `{item['stage']}` / {item['event']}"
            )
        )



def main() -> None:
    st.set_page_config(page_title="変質する自己相似ダッシュボード", layout="wide")
    initialize_state()

    st.title("未確定自己相似変質ダッシュボード")
    st.caption("観測するたびに構造が変質し、同じ形は維持されない。")

    controls = st.columns((1, 1, 2))
    with controls[0]:
        if st.button("観測を実行", type="primary", use_container_width=True):
            event = apply_mutation(observe_uncertain_self_similarity())
            st.toast(event, icon="🌀")
    with controls[1]:
        if st.button("状態を初期化", use_container_width=True):
            for key in ["observations", "stage", "resonance", "history", "seed"]:
                st.session_state.pop(key, None)
            initialize_state()
            st.rerun()
    with controls[2]:
        st.write(
            "観測圧力が高いと段階上昇、低いと段階下降。"
            "閾値付近では同じ観測でも違う形へ遷移します。"
        )

    overview = st.columns(4)
    overview[0].metric("観測回数", st.session_state.observations)
    overview[1].metric("変質段階", st.session_state.stage)
    overview[2].metric("共鳴率", f"{st.session_state.resonance:.3f}")
    if st.session_state.history:
        last_pressure = st.session_state.history[0]["pressure"]
        overview[3].metric("最新圧力", f"{last_pressure:.3f}")
    else:
        overview[3].metric("最新圧力", "---")

    st.divider()
    render_structure(st.session_state.stage)
    st.divider()
    render_history()


if __name__ == "__main__":
    main()
