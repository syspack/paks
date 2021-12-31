ARG ubuntu_version
FROM ghcr.io/rse-ops/ubuntu:$ubuntu_version

# docker build --build-arg ubuntu_version=20.04 -t ghcr.io/syspack/paks-ubuntu-20.04 .

# Build all software with debug flags!
ENV SPACK_ADD_DEBUG_FLAGS=true

COPY docker/entrypoint.sh /entrypoint.sh

# Install latest version of Paks
RUN git clone https://github.com/syspack/paks /opt/paks && \
    cd /opt/paks && \
    python3 -m pip install .
   
ENV SPACK_ROOT=/opt/spack    

ENTRYPOINT ["/entrypoint.sh"]
