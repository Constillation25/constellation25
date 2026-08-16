FROM mcr.microsoft.com/devcontainers/javascript-node:0-22-bullseye

RUN mkdir -p /home/node/constellation25/{agents,core/readdo,gateway/retail,gateway/online,db/migrations,logs/forensic} \
    && mkdir -p /home/node/c25_ipc/{pending,completed,failed}

ENV C25_ROOT=/home/node/constellation25
ENV IPC_DIR=/home/node/c25_ipc/pending

RUN npm install -g typescript ts-node vitest

WORKDIR ${C25_ROOT}
