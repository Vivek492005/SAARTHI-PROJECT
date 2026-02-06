# build script for cursorControl package

# update and upgrade packages
sudo apt-get -y update
sudo apt-get -y upgrade

# Install Dependencies
sudo apt-get -y install tar
# sudo apt-get -y install qt5-default

# download OpenCV from Github
mkdir -p third_party && cd third_party
git clone https://github.com/opencv/opencv.git
cd opencv
git checkout 4.5.1
cd ..

# download opencv_contrib from Github
# git clone https://github.com/opencv/opencv_contrib.git
# cd opencv_contrib
# git checkout 4.5.1
# cd ..

# compile and Install OpenCV with contrib
# create build directory inside opencv directory
cd opencv
mkdir -p build
cd build

# run CMake with the following options
cmake -D CMAKE_BUILD_TYPE=RELEASE \
      -D INSTALL_CREATE_DISTRIB=ON \
      -D BUILD_SHARED_LIBS=ON \
      -D CMAKE_INSTALL_PREFIX=/usr/local \
      -D BUILD_LIST=core,imgproc,objdetect,highgui,videoio \
      -D WITH_TBB=ON \
      -D WITH_V4L=ON \
      -D WITH_QT=OFF \
      -D WITH_OPENGL=ON  ..

# compile and install
make -j4
sudo make install
sudo sh -c 'echo "/usr/local/lib" >> /etc/ld.so.conf.d/opencv.conf'
sudo ldconfig

# install Boost
cd ..
cd ..
wget https://boostorg.jfrog.io/artifactory/main/release/1.76.0/source/boost_1_76_0.tar.gz
tar -xzf boost_1_76_0.tar.gz

# configure cmake for project build
cd ..
mkdir -p build
cmake -B build ../cursorControl

# build the project
cmake --build build

# install the project
mkdir -p install
cmake --install build --config Debug --prefix install