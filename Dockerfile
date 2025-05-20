FROM ubuntu:22.04

# 安装基本工具
RUN apt-get update && apt-get install -y \
    build-essential \
    gcc-aarch64-linux-gnu \
    g++-aarch64-linux-gnu \
    gcc-arm-linux-gnueabihf \
    g++-arm-linux-gnueabihf \
    musl-tools \
    wget \
    vim \
    git \
    make \
    cmake \
    autoconf \
    automake \
    python3 \
    libtool \
    pkg-config \
    zlib1g-dev \
    && rm -rf /var/lib/apt/lists/*

# 创建工具链安装目录
RUN mkdir -p /opt/openwrt/toolchains

RUN wget -O /tmp/openwrt-toolchain.tar.xz \
    https://downloads.openwrt.org/releases/23.05.5/targets/x86/64/openwrt-toolchain-23.05.5-x86-64_gcc-12.3.0_musl.Linux-x86_64.tar.xz \
    && tar -xJf /tmp/openwrt-toolchain.tar.xz -C /opt/openwrt/toolchains \
    && mv /opt/openwrt/toolchains/openwrt-toolchain-23.05.5-x86-64_gcc-12.3.0_musl.Linux-x86_64 /opt/openwrt/toolchains/x86_64 \
    && rm /tmp/openwrt-toolchain.tar.xz

RUN wget -O /tmp/openwrt-toolchain-imx-cortexa7.tar.xz \
    https://downloads.openwrt.org/releases/23.05.5/targets/imx/cortexa7/openwrt-toolchain-23.05.5-imx-cortexa7_gcc-12.3.0_musl_eabi.Linux-x86_64.tar.xz \
    && tar -xJf /tmp/openwrt-toolchain-imx-cortexa7.tar.xz -C /opt/openwrt/toolchains \
    && mv /opt/openwrt/toolchains/openwrt-toolchain-23.05.5-imx-cortexa7_gcc-12.3.0_musl_eabi.Linux-x86_64 /opt/openwrt/toolchains/arm32 \
    && rm /tmp/openwrt-toolchain-imx-cortexa7.tar.xz

RUN wget -O /tmp/openwrt-toolchain-rockchip-armv8.tar.xz \
    https://downloads.openwrt.org/releases/23.05.5/targets/rockchip/armv8/openwrt-toolchain-23.05.5-rockchip-armv8_gcc-12.3.0_musl.Linux-x86_64.tar.xz \
    && tar -xJf /tmp/openwrt-toolchain-rockchip-armv8.tar.xz -C /opt/openwrt/toolchains \
    && mv /opt/openwrt/toolchains/openwrt-toolchain-23.05.5-rockchip-armv8_gcc-12.3.0_musl.Linux-x86_64 /opt/openwrt/toolchains/arm64 \
    && rm /tmp/openwrt-toolchain-rockchip-armv8.tar.xz

RUN wget -O /tmp/openwrt-toolchain-ath79-generic.tar.xz \
    https://downloads.openwrt.org/releases/23.05.5/targets/ath79/generic/openwrt-toolchain-23.05.5-ath79-generic_gcc-12.3.0_musl.Linux-x86_64.tar.xz \
    && tar -xJf /tmp/openwrt-toolchain-ath79-generic.tar.xz -C /opt/openwrt/toolchains \
    && mv /opt/openwrt/toolchains/openwrt-toolchain-23.05.5-ath79-generic_gcc-12.3.0_musl.Linux-x86_64 /opt/openwrt/toolchains/mips32 \
    && rm /tmp/openwrt-toolchain-ath79-generic.tar.xz

ENV PATH="/opt/openwrt/toolchains/x86_64/toolchain-x86_64_gcc-12.3.0_musl/bin:/opt/openwrt/toolchains/arm32/toolchain-arm_cortex-a7+neon-vfpv4_gcc-12.3.0_musl_eabi/bin:/opt/openwrt/toolchains/arm64/toolchain-aarch64_generic_gcc-12.3.0_musl/bin:/opt/openwrt/toolchains/mips32/toolchain-mips_24kc_gcc-12.3.0_musl/bin:${PATH}"

# 设置工作目录
WORKDIR /workspace

# 默认命令
CMD ["/bin/bash"]
