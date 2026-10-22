#!/usr/bin/env bash
# Run this on a machine WITH an NVIDIA GPU + CUDA toolkit. Not Termux.
set -euo pipefail
ARCH="${1:-sm_80}"
nvcc -O3 -arch="$ARCH" lut_gemm.cu -o lut_gemm
echo "[+] built ./lut_gemm for $ARCH"
echo "[+] benchmark: ./lut_gemm 512 && ./lut_gemm 2048 && ./lut_gemm 4096"
echo "[+] compare vs cuBLAS: nvidia-smi dmon -s u  (watch SM vs MEM utilization)"
