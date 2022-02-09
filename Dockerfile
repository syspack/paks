ARG ubuntu_version
FROM ubuntu:$ubuntu_version

# docker build --build-arg ubuntu_version=20.04 -t ghcr.io/syspack/paks-ubuntu-20.04 .

RUN apt-get update && apt-get install -y python3-dev python3-pip
# install oras so we don't need to bootstrap
# RUN curl -LO https://github.com/oras-project/oras/releases/download/v0.12.0/oras_0.12.0_linux_amd64.tar.gz && \
#    mkdir -p oras-install/ && \
#    tar -zxf oras_0.12.0_*.tar.gz -C oras-install/ && \
#    mv oras-install/oras /usr/local/bin/ && \
#    rm -rf oras_0.12.0_*.tar.gz oras-install/

# The entrypoint.sh is called during the ci
WORKDIR /opt/paks
COPY . /opt/paks
RUN python3 -m pip install .
ENTRYPOINT ["/bin/bash"]
