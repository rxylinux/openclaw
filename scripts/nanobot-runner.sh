#!/bin/bash
# nanobot 子 agent 启动脚本

# 激活虚拟环境
source /root/.nanobot-env/bin/activate

# 运行 nanobot
nanobot agent "$@"
