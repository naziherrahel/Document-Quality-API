FROM nvidia/cuda:12.1.1-cudnn8-runtime-ubuntu22.04

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DEBIAN_FRONTEND=noninteractive \
    PIP_NO_CACHE_DIR=1 \
    PIP_RETRIES=5 \
    PIP_TIMEOUT=60

# System dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    software-properties-common \
    curl \
    && add-apt-repository ppa:deadsnakes/ppa \
    && apt-get install -y \
    python3.9 \
    python3.9-dev \
    python3.9-distutils \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxrender1 \
    libxext6 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install pip with retries
RUN curl --retry 5 -sS https://bootstrap.pypa.io/get-pip.py -o get-pip.py \
    && python3.9 get-pip.py \
    && rm get-pip.py

# Install PaddlePaddle with fallback
RUN python3.9 -m pip install --retries=$PIP_RETRIES \
    paddlepaddle-gpu==2.6.1.post120 \
    -f https://www.paddlepaddle.org.cn/whl/linux/mkl/avx/stable.html \
    || python3.9 -m pip install --retries=$PIP_RETRIES \
    paddlepaddle-gpu==2.6.1 -i https://mirror.baidu.com/pypi/simple

# Install PyTorch
RUN python3.9 -m pip install --retries=$PIP_RETRIES \
    torch==2.1.2+cu121 \
    torchvision==0.16.2+cu121 \
    --extra-index-url https://download.pytorch.org/whl/cu121

# Install requirements with retries
WORKDIR /app
COPY requirements.txt .
RUN python3.9 -m pip install --retries=$PIP_RETRIES -r requirements.txt

COPY . .

EXPOSE 8000
CMD ["python3", "-m", "uvicorn", "api.app:app", "--host", "0.0.0.0", "--port", "8000"]