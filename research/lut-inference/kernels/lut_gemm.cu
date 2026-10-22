// LUT-GEMM: 4-bit quantized matmul via shared-memory lookup table
// Target: any CUDA GPU with >=48KB shared memory per SM
// Build: nvcc -O3 -arch=sm_80 lut_gemm.cu -o lut_gemm

#include <cuda_runtime.h>
#include <cstdio>
#include <cstdlib>
#include <cmath>

#define LUT_DIM   16      // 4-bit quantization levels per operand
#define LUT_SIZE  (LUT_DIM * LUT_DIM)   // 256 entries x 4B = 1KB
#define TILE_M    64
#define TILE_N    64
#define TILE_K    32

__global__ void lut_gemm_kernel(
    const unsigned char* __restrict__ Aq,   // 4-bit codes for A (row-major MxK)
    const unsigned char* __restrict__ Bq,   // 4-bit codes for B (col-major KxN)
    const float* __restrict__ lut,          // LUT_SIZE product table
    float* __restrict__ C, int M, int N, int K)
{
    __shared__ float s_lut[LUT_SIZE];
    __shared__ unsigned char s_a[TILE_M][TILE_K];
    __shared__ unsigned char s_b[TILE_K][TILE_N];

    int tid = threadIdx.x + threadIdx.y * blockDim.x;
    if (tid < LUT_SIZE) s_lut[tid] = lut[tid];
    __syncthreads();

    int row = blockIdx.y * TILE_M + threadIdx.y;
    int col = blockIdx.x * TILE_N + threadIdx.x;
    float acc = 0.0f;

    for (int k0 = 0; k0 < K; k0 += TILE_K) {
        if (row < M && (k0 + threadIdx.x) < K) s_a[threadIdx.y][threadIdx.x] = Aq[row * K + k0 + threadIdx.x];
        if (col < N && (k0 + threadIdx.y) < K) s_b[threadIdx.y][threadIdx.x] = Bq[(k0 + threadIdx.y) * N + col];
        __syncthreads();

        #pragma unroll
        for (int k = 0; k < TILE_K; ++k) {
            unsigned char key = (unsigned char)((s_a[threadIdx.y][k] << 4) | s_b[k][threadIdx.x]);
            acc += s_lut[key];          // 1 SMEM load, 1 add -> no FMA, no DRAM
        }
        __syncthreads();
    }
    if (row < M && col < N) C[row * N + col] = acc;
}

int main(int argc, char** argv) {
    int M = argc > 1 ? atoi(argv[1]) : 512;
    int N = M, K = M;
    size_t ab_bytes = (size_t)M * K, c_bytes = (size_t)M * N * sizeof(float);

    unsigned char *hA = (unsigned char*)malloc(ab_bytes), *hB = (unsigned char*)malloc(ab_bytes);
    float *hC = (float*)malloc(c_bytes), *hLUT = (float*)malloc(LUT_SIZE * sizeof(float));
    for (size_t i = 0; i < ab_bytes; ++i) { hA[i] = rand() % LUT_DIM; hB[i] = rand() % LUT_DIM; }
    for (int i = 0; i < LUT_SIZE; ++i) hLUT[i] = (float)(i / LUT_DIM) * (float)(i % LUT_DIM) * 0.01f;

    unsigned char *dA, *dB; float *dC, *dLUT;
    cudaMalloc(&dA, ab_bytes); cudaMalloc(&dB, ab_bytes);
    cudaMalloc(&dC, c_bytes);  cudaMalloc(&dLUT, LUT_SIZE * sizeof(float));
    cudaMemcpy(dA, hA, ab_bytes, cudaMemcpyHostToDevice);
    cudaMemcpy(dB, hB, ab_bytes, cudaMemcpyHostToDevice);
    cudaMemcpy(dLUT, hLUT, LUT_SIZE * sizeof(float), cudaMemcpyHostToDevice);

    dim3 block(32, 32), grid((N + TILE_N - 1) / TILE_N, (M + TILE_M - 1) / TILE_M);
    cudaEvent_t s, e; cudaEventCreate(&s); cudaEventCreate(&e);

    lut_gemm_kernel<<<grid, block>>>(dA, dB, dLUT, dC, M, N, K);   // warmup
    cudaDeviceSynchronize();
    cudaEventRecord(s);
    for (int i = 0; i < 50; ++i) lut_gemm_kernel<<<grid, block>>>(dA, dB, dLUT, dC, M, N, K);
    cudaEventRecord(e); cudaEventSynchronize(e);

    float ms = 0; cudaEventElapsedTime(&ms, s, e); ms /= 50.0f;
    double flops = 2.0 * M * N * K;
    double bytes = (double)(2 * ab_bytes + c_bytes);
    printf("M=N=K=%d  time=%.4f ms  %.1f GFLOP/s  %.1f GB/s  AI=%.2f FLOP/byte\n",
           M, ms, flops / ms / 1e6, bytes / ms / 1e6, flops / bytes);
    cudaFree(dA); cudaFree(dB); cudaFree(dC); cudaFree(dLUT);
    free(hA); free(hB); free(hC); free(hLUT);
    return 0;
}
