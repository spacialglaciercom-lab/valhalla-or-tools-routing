FROM ubuntu:22.04

RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    liblz4-dev \
    libboost-all-dev \
    libcurl4-openssl-dev \
    libgeos-dev \
    libgeos++-dev \
    libprotobuf-dev \
    protobuf-compiler \
    libsqlite3-dev \
    libspatialite-dev \
    libtiff-dev \
    libgeotiff-dev \
    libluajit-5.1-dev \
    libssl-dev \
    python3-dev \
    python3-pip \
    software-properties-common

# Install CMake 3.26+ from Kitware APT repo
RUN curl -fsSL https://apt.kitware.com/keys/kitware-archive-latest.asc | gpg --dearmor -o /usr/share/keyrings/kitware-archive-keyring.gpg && \
    echo 'deb [signed-by=/usr/share/keyrings/kitware-archive-keyring.gpg] https://apt.kitware.com/ubuntu/ jammy main' > /etc/apt/sources.list.d/kitware.list && \
    apt-get update && apt-get install -y cmake

RUN git clone --depth 1 https://github.com/valhalla/valhalla.git /valhalla

WORKDIR /valhalla

RUN mkdir build && cd build && \
    cmake .. -DCMAKE_BUILD_TYPE=Release -DENABLE_SERVICES=OFF -DENABLE_HTTP_SERVER=OFF -DENABLE_PYTHON_BINDINGS=OFF && \
    make -j$(nproc) && \
    make install && \
    ldconfig

WORKDIR /

CMD ["/bin/bash"]