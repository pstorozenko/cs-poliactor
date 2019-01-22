# This is a sample Dockerfile you can modify to deploy your own app based on face_recognition

FROM python:3.6-slim-stretch

RUN apt-get -y update
RUN apt-get install -y --fix-missing \
    build-essential \
    cmake \
    gfortran \
    git \
    wget \
    curl \
    graphicsmagick \
    libgraphicsmagick1-dev \
    libatlas-dev \
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
    git clone -b 'v19.9' --single-branch https://github.com/davisking/dlib.git dlib/ && \
    cd  dlib/ && \
    python3 setup.py install  --no USE_AVX_INSTRUCTIONS --no DLIB_USE_CUDA


# The rest of this file just runs an example script.

# If you wanted to use this Dockerfile to run your own app instead, maybe you would do this:
# COPY . /root/your_app_or_whatever
# RUN cd /root/your_app_or_whatever && \
#     pip3 install -r requirements.txt
# RUN whatever_command_you_run_to_start_your_app

# Install Python
COPY requirements.txt .
RUN pip3 install -r requirements.txt && \
    git clone https://github.com/ageitgey/face_recognition.git /root/face_recognition && \
    cd /root/face_recognition && \
    python3 setup.py install


# COPY face_recognition /root/face_recognition
# RUN cd /root/face_recognition && \
#     # pip3 install -r requirements.txt && \
#     python3 setup.py install

# CMD cd /root/face_recognition/examples && \
#     python3 recognize_faces_in_pictures.py

# Expose port for connection
EXPOSE 8000

# Add requirements.txt
RUN mkdir /app
ENV HOME /app
WORKDIR /app

ENTRYPOINT ["python3", "app.py"]
