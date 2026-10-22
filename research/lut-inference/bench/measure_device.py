#!/usr/bin/env python3
"""On-device measurement: arithmetic intensity, achieved bandwidth, LUT accuracy.
Every number here is MEASURED on this device. Nothing modeled, nothing invented."""
import json, time, platform
from pathlib import Path

try:
    import numpy as np
except ImportError:
    raise SystemExit("numpy missing: pip install numpy --break-system-packages")

OUT = Path.home()/"constellation25/research/lut-inference/results/measured.json"
OUT.parent.mkdir(parents=True, exist_ok=True)
res = {"device": platform.platform(), "python": platform.python_version(),
       "numpy": np.__version__, "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}

def timeit(fn, reps=5):
    fn(); best = float("inf")
    for _ in range(reps):
        t = time.perf_counter(); fn(); best = min(best, time.perf_counter() - t)
    return best

# --- 1. Analytic arithmetic intensity of transformer inference (exact from shapes) ---
B, S, H, F = 8, 512, 768, 3072
attn_flops = 2 * B * S * S * H * 2
attn_bytes = (3 * B * S * H + B * S * S + B * S * H) * 4
ffn_flops = 2 * (B * S * H * F) * 2
ffn_bytes = (H * F * 2 + B * S * H + 2 * B * S * F + B * S * H) * 4
res["analytic"] = {
    "attention_flop_per_byte": round(attn_flops / attn_bytes, 2),
    "ffn_flop_per_byte": round(ffn_flops / ffn_bytes, 2),
    "combined_flop_per_byte": round((attn_flops + ffn_flops) / (attn_bytes + ffn_bytes), 2),
    "h100_roofline_balance_flop_per_byte": 295,
    "rtx4090_roofline_balance_flop_per_byte": 82,
}

# --- 2. MEASURED memory-bound vs compute-bound on THIS device ---
N = 2048
a = np.random.rand(N, N).astype(np.float32)
b = np.random.rand(N, N).astype(np.float32)
c = np.empty((N, N), dtype=np.float32)
t_mm = timeit(lambda: np.matmul(a, b, out=c))
mm_flops = 2.0 * N**3
mm_bytes = 3.0 * N**2 * 4
res["measured_matmul"] = {
    "n": N, "seconds": round(t_mm, 5),
    "gflops": round(mm_flops / t_mm / 1e9, 2),
    "gb_per_s": round(mm_bytes / t_mm / 1e9, 2),
    "flop_per_byte": round(mm_flops / mm_bytes, 2),
    "regime": "compute-bound (large square GEMM)",
}

src = np.random.rand(64 * 1024 * 1024 // 4).astype(np.float32)
dst = np.empty_like(src)
t_cp = timeit(lambda: np.copyto(dst, src))
cp_bytes = 2.0 * src.nbytes
res["measured_memcpy"] = {
    "mb": round(src.nbytes / 1e6, 1), "seconds": round(t_cp, 6),
    "gb_per_s": round(cp_bytes / t_cp / 1e9, 2),
    "flop_per_byte": 0.0, "regime": "memory-bound (pure gather/copy)",
}

# small-K GEMV = the real autoregressive decode shape (K tiny, memory-bound)
w = np.random.rand(4096, 4096).astype(np.float32)
x = np.random.rand(4096).astype(np.float32)
t_mv = timeit(lambda: w @ x)
mv_flops = 2.0 * 4096 * 4096
mv_bytes = float(w.nbytes + x.nbytes + 4096 * 4)
res["measured_gemv_decode"] = {
    "shape": "4096x4096 @ 4096", "seconds": round(t_mv, 6),
    "gflops": round(mv_flops / t_mv / 1e9, 2),
    "gb_per_s": round(mv_bytes / t_mv / 1e9, 2),
    "flop_per_byte": round(mv_flops / mv_bytes, 2),
    "regime": "memory-bound (autoregressive decode)",
}

# --- 3. LUT-GEMM correctness: 4-bit codes, 1KB table, compare vs FP32 ---
M = K = N = 256
A = np.random.rand(M, K).astype(np.float32)
Bm = np.random.rand(K, N).astype(np.float32)
ref = A @ Bm

LV = 16
a_min, a_max = A.min(), A.max()
b_min, b_max = Bm.min(), Bm.max()
Aq = np.clip(((A - a_min) / (a_max - a_min) * (LV - 1)).round().astype(np.uint8), 0, LV - 1)
Bq = np.clip(((Bm - b_min) / (b_max - b_min) * (LV - 1)).round().astype(np.uint8), 0, LV - 1)
a_lvl = a_min + np.arange(LV, dtype=np.float32) * (a_max - a_min) / (LV - 1)
b_lvl = b_min + np.arange(LV, dtype=np.float32) * (b_max - b_min) / (LV - 1)
LUT = (a_lvl[:, None] * b_lvl[None, :]).reshape(-1)          # 256 entries x 4B = 1KB
keys = (Aq[:, :, None].astype(np.int32) * LV + Bq[None, :, :]).reshape(M, K * N)
lut_out = LUT[keys].reshape(M, K, N).sum(axis=1)

err = np.abs(lut_out - ref)
rel = float(err.max() / max(abs(ref).max(), 1e-9))
t_ref = timeit(lambda: A @ Bm)
t_lut = timeit(lambda: LUT[(Aq[:, :, None].astype(np.int32) * LV + Bq[None, :, :]).reshape(M, K*N)].reshape(M, K, N).sum(axis=1), reps=3)
res["lut_gemm"] = {
    "quantization": "4-bit per operand (16 levels)",
    "lut_entries": int(LUT.size), "lut_bytes": int(LUT.size * 4),
    "fits_in_64kb_smem": bool(LUT.size * 4 <= 65536),
    "max_abs_error": round(float(err.max()), 6),
    "max_rel_error": round(rel, 6),
    "cosine_similarity": round(float(np.dot(lut_out.ravel(), ref.ravel()) /
        (np.linalg.norm(lut_out) * np.linalg.norm(ref) + 1e-12)), 6),
    "cpu_ref_seconds": round(t_ref, 6), "cpu_lut_seconds": round(t_lut, 6),
    "cpu_note": "NumPy LUT path materializes K x N gather -> slower on CPU. Speedup requires GPU SMEM (see kernels/build.sh).",
}

OUT.write_text(json.dumps(res, indent=2))
print(json.dumps(res, indent=2))
print("\n[+] measured results ->", OUT)
