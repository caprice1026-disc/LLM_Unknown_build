import sqlite3
from datetime import datetime

import numpy as np
import pandas as pd
import streamlit as st

DB_PATH = "xeno_resonance.db"


def ensure_db() -> None:
    """履歴保存用のSQLiteテーブルを初期化する。"""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS resonance_runs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            created_at TEXT NOT NULL,
            seed INTEGER NOT NULL,
            depth INTEGER NOT NULL,
            resonance REAL NOT NULL,
            decoherence REAL NOT NULL,
            iterations INTEGER NOT NULL,
            coherence_ratio REAL NOT NULL,
            spectral_focus REAL NOT NULL,
            phase_stability REAL NOT NULL
        )
        """
    )
    conn.commit()
    conn.close()


def generate_xeno_echo(
    points: int,
    depth: int,
    resonance: float,
    decoherence: float,
    seed: int,
) -> tuple[np.ndarray, np.ndarray]:
    """ゼノフラクタル残響を模した信号を生成する。"""
    rng = np.random.default_rng(seed)
    t = np.linspace(0.0, 12.0, points)

    signal = np.zeros_like(t)
    base_freq = 0.8 + resonance * 1.3

    for layer in range(1, depth + 1):
        freq = base_freq * (1.5 ** (layer - 1))
        amp = (0.68 ** layer) * (1.0 + resonance * 0.4)
        damping = np.exp(-t * (0.06 * layer + decoherence * 0.18))
        signal += amp * np.sin(2 * np.pi * freq * t + layer * 0.21) * damping

    fractal_mod = np.sin(2 * np.pi * (base_freq / 3.0) * t) * np.cos(2 * np.pi * base_freq * t)
    noise = rng.normal(0.0, 0.06 + decoherence * 0.14, size=points)

    raw_echo = signal + 0.32 * fractal_mod + noise
    return t, raw_echo


def distill_coherence(
    raw_echo: np.ndarray,
    resonance: float,
    decoherence: float,
    iterations: int,
) -> tuple[np.ndarray, np.ndarray]:
    """周波数領域でコヒーレント成分を強調して蒸留信号を作る。"""
    spectrum = np.fft.rfft(raw_echo)
    magnitude = np.abs(spectrum)

    median_mag = np.median(magnitude) + 1e-8
    focus = 1.0 + resonance * 2.6
    gate = 1.0 / (1.0 + np.exp(-(magnitude / median_mag - focus)))

    phase_alignment = np.exp(-decoherence * 0.8)
    phase = np.angle(spectrum)
    aligned_phase = phase * phase_alignment

    distilled = magnitude * gate * np.exp(1j * aligned_phase)
    distilled_wave = np.fft.irfft(distilled, n=raw_echo.size)

    for _ in range(max(1, iterations - 1)):
        distilled_wave = 0.7 * distilled_wave + 0.3 * np.roll(distilled_wave, 1)

    return distilled_wave, gate


def compute_metrics(raw_echo: np.ndarray, distilled_echo: np.ndarray, gate: np.ndarray) -> dict[str, float]:
    """蒸留結果の指標を返す。"""
    raw_energy = float(np.sum(raw_echo**2) + 1e-8)
    distilled_energy = float(np.sum(distilled_echo**2))

    coherence_ratio = distilled_energy / raw_energy
    spectral_focus = float(np.mean(gate))
    phase_stability = float(1.0 / (1.0 + np.std(raw_echo - distilled_echo)))

    return {
        "coherence_ratio": coherence_ratio,
        "spectral_focus": spectral_focus,
        "phase_stability": phase_stability,
    }


def save_run(
    seed: int,
    depth: int,
    resonance: float,
    decoherence: float,
    iterations: int,
    metrics: dict[str, float],
) -> None:
    """現在の実行パラメータと指標をSQLiteに保存する。"""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO resonance_runs (
            created_at,
            seed,
            depth,
            resonance,
            decoherence,
            iterations,
            coherence_ratio,
            spectral_focus,
            phase_stability
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            datetime.utcnow().isoformat(timespec="seconds") + "Z",
            seed,
            depth,
            resonance,
            decoherence,
            iterations,
            metrics["coherence_ratio"],
            metrics["spectral_focus"],
            metrics["phase_stability"],
        ),
    )
    conn.commit()
    conn.close()


def fetch_recent_runs(limit: int = 8) -> pd.DataFrame:
    """直近の保存履歴を取得する。"""
    conn = sqlite3.connect(DB_PATH)
    query = """
        SELECT
            created_at,
            seed,
            depth,
            resonance,
            decoherence,
            iterations,
            coherence_ratio,
            spectral_focus,
            phase_stability
        FROM resonance_runs
        ORDER BY id DESC
        LIMIT ?
    """
    df = pd.read_sql_query(query, conn, params=(limit,))
    conn.close()
    return df


def main() -> None:
    st.set_page_config(page_title="ゼノフラクタル残響蒸留器", layout="wide")
    st.title("ゼノフラクタルの残響をコヒーレントに蒸留する実験室")
    st.caption("残響を生成し、位相とスペクトルの一貫性を高める蒸留を試せます。")

    ensure_db()

    st.sidebar.header("生成パラメータ")
    seed = st.sidebar.number_input("Seed", min_value=0, max_value=999999, value=42, step=1)
    depth = st.sidebar.slider("フラクタル深度", min_value=2, max_value=10, value=6)
    resonance = st.sidebar.slider("共鳴強度", min_value=0.1, max_value=1.0, value=0.6, step=0.05)
    decoherence = st.sidebar.slider("非コヒーレンス", min_value=0.0, max_value=1.0, value=0.25, step=0.05)
    iterations = st.sidebar.slider("蒸留反復", min_value=1, max_value=8, value=3)
    points = st.sidebar.select_slider("サンプル数", options=[512, 1024, 2048], value=1024)

    t, raw_echo = generate_xeno_echo(points, depth, resonance, decoherence, int(seed))
    distilled_echo, gate = distill_coherence(raw_echo, resonance, decoherence, iterations)
    metrics = compute_metrics(raw_echo, distilled_echo, gate)

    col1, col2, col3 = st.columns(3)
    col1.metric("Coherence Ratio", f"{metrics['coherence_ratio']:.3f}")
    col2.metric("Spectral Focus", f"{metrics['spectral_focus']:.3f}")
    col3.metric("Phase Stability", f"{metrics['phase_stability']:.3f}")

    chart_df = pd.DataFrame(
        {
            "t": t,
            "raw_echo": raw_echo,
            "distilled_echo": distilled_echo,
        }
    ).set_index("t")

    st.subheader("波形比較")
    st.line_chart(chart_df)

    st.subheader("周波数ゲート分布")
    gate_df = pd.DataFrame({"bin": np.arange(gate.size), "gate": gate})
    st.area_chart(gate_df.set_index("bin"))

    if st.button("この蒸留結果を履歴に保存", type="primary"):
        save_run(int(seed), depth, resonance, decoherence, iterations, metrics)
        st.success("履歴へ保存しました。")

    st.subheader("直近の蒸留履歴")
    history = fetch_recent_runs()
    if history.empty:
        st.info("履歴はまだありません。パラメータを調整して保存してください。")
    else:
        st.dataframe(history, use_container_width=True)


if __name__ == "__main__":
    main()
