FROM ubuntu:xenial
# you might have to update your outdated clang

RUN sudo add-apt-repository -y ppa:ubuntu-toolchain-r/test
RUN sudo apt-get update -y
RUN sudo apt-get install -y gcc-6 g++-6 clang-3.8
ENV CXX="clang++-3.8"
ENV CC="clang-3.8"

# install mapnik
RUN git clone https://github.com/mapnik/mapnik mapnik-3.x --depth 10 &&
WORKDIR mapnik-3.x 
RUN git submodule update --init
RUN sudo apt-get install python zlib1g-dev clang make pkg-config curl
RUN source bootstrap.sh
RUN ./configure CUSTOM_CXXFLAGS="-D_GLIBCXX_USE_CXX11_ABI=0" CXX=${CXX} CC=${CC}
RUN make && make test && sudo make install