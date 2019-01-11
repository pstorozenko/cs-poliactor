FROM ubuntu:18.10
 
# Update OS and create superuser
RUN apt-get update && \
    apt-get -y upgrade

RUN apt-get -y install python3-dev python3-pip

RUN apt-get install -y --fix-missing \
    build-essential \
    cmake \
    gfortran \
    git \
    wget \
    curl \
    graphicsmagick \
    libgraphicsmagick1-dev \
    libatlas-base-dev \
    libavcodec-dev \
    libavformat-dev \
    libgtk2.0-dev \
    libjpeg-dev \
    liblapack-dev \
    libswscale-dev \
    pkg-config \
    python3-dev \
    python3-numpy \
    software-properties-common \
    zip \
    && apt-get clean && rm -rf /tmp/* /var/tmp/*

RUN cd ~ && \
    mkdir -p dlib && \
    git clone --single-branch https://github.com/davisking/dlib.git dlib/ && \
    cd  dlib/ && \
    mkdir build && \
    cd build && \
    cmake .. && \
    cmake --build . && \
    cd .. && \
    python3 setup.py install --yes

# Install Python
COPY reqs.txt .
RUN pip3 install -r reqs.txt

# Expose port for connection
EXPOSE 6113

# Add requirements.txt
RUN mkdir /app
ENV HOME /app
WORKDIR /app

ENTRYPOINT ["python3", "app.py"]