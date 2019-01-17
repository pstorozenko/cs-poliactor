# Your face seems famous!

Have you ever thought which actor are you the most similar to? That's exactly what our app will tell you!

> dodać fotkę dwóch osób podobnych i że dla jednego zwróciło drugie> // Pasz

# Installation

The app can be run locally on your own machine. Due to `face_recognition` package requirements macOS and Linux machines are supported.

Local requirements:

- Python >= 3.6
- [dlib](http://dlib.net/)
- numpy==1.15
- pandas==0.23.4
- Flask==1.0.2
- Flask-SocketIO==3.0.2
- Pillow==5.3.0
- eventlet==0.24.1
- face_recognition==1.2.3
- matplotlib==3.0.2
- scikit-learn==0.20.0

All needed Python packages are listed in `reqs.txt` file.

Since `dlib` and `face_recognition` [installation](https://github.com/ageitgey/face_recognition#installation) can be problematic in some cases, we highly recommend using Docker containers. `Dockerfile` as well as `docker-compose` files can be found in the `docker` directory.

To run application via Docker go to the `Docker` directory and run in the console:

```docker-compose up```

For more details visit [Docker documentation](https://docs.docker.com/get-started/)

By default app is available under `http://localhost:6113`

# Usage

![](images/poliaktor_screen.png)

After reaching proper URL, give the app an permissions to your webcam. Then all you have to do is wait to see results.

On the bottom left webcam stream will be displayed with most similar actor's image and name above it. On the right there will be plot showing position of current embedding of captured face (with respect to the average).

On topmost left position there is "control center". The number in the box determines number of webcam frames that are averaged while searching the most similar actor's photo. By clicking the `Reset` button you can reset plot and averaging process.

If no or more than one faces are detected no result will be displayed. After 15 consequent frames with no result, plot and averaging resets automatically.

# Technical info

Our application is a web app with client server architecture and communication over web sockets.

Client side is responsible only for capturing frames from webcam stream which is then send to the server, displaying results and controlling some runtime parameters. We've used standard, plain HTML/CSS/JS stack alongside with [socket.io](https://socket.io/) library.  

All computation is done at the server side. Server is written in [Flask](http://flask.pocoo.org/) with help of [Flask-socketIO](https://flask-socketio.readthedocs.io/en/latest/) to allow communication over web sockets.

![](images/diagram.png)

For face detection and encoding [face_recognition](https://github.com/ageitgey/face_recognition) package is used. Here we add a brief description of what is going on under the hood but for more (first hand) information about methods and models take a look at this [blog post](https://medium.com/@ageitgey/machine-learning-is-fun-part-4-modern-face-recognition-with-deep-learning-c3cffc121d78).

1. Face detection
   - convert picture to grayscale
   - compute HOG ([Histogram of Oriented Gradients](https://lear.inrialpes.fr/people/triggs/pubs/Dalal-cvpr05.pdf)) on the 16x16 grid
   - find HOG face pattern
2. Posing and Projecting Faces
   - compute 68 face [landmark points](http://www.csc.kth.se/~vahidk/papers/KazemiCVPR14.pdf)
   - find affine transformations to align photo to perfectly centered face pattern
3. Faces encoding
   - get pretrained neural network e.g. from [OpenFace](https://cmusatyalab.github.io/openface/) library
   - encode your faces from your database using this network
4. Finding the most similar face
   - train any classifier to classify faces from your database
   - classify new images

Feces are compared with precomputed representations of predefined set of **4062** images (**289** different actors) using KNN algorithm with $n = 1$.

# Processing methodology

[//]: # (nazwa do zmiany)

## Finding the most similar actor

`face_recognition` package is capable of finding the most similar photo on the fly, but in out application we have to take some performance aspects into account. Based on info provided by package creators we've decided to use KNN classifier for that purpose.

Talking about distance. The plot underneath depicts distribution of distances between embedding of all frames recorded for a person (based on 5 different people) and distances between that frames and returned, most similar actor.

![](images/distribution.png)

Since the neural network was trained to find exact person, not the one the most similar it's easy to notice two things (regardless units and scale):

- photos of the same person can differ a lot. It is because we ask people not to be steady while recording as well as laptop camera gives quite noisy images.
- most of returned pictures of actors are in specific, narrow range.

Network is able to spot subtle differences in faces, but what is more visible, works great in terms of distinguishing people.

## Stability issues

From the beginning of project stability of responses were the biggest concern. Webcam images usually have poor quality which is highly dependent on light conditions. What is more, photos used in the project are quite diverse even looking at a single actor.

During first tries, every response shows different person, even when we tried not to move our faces. Due to the fact that KNN algorithm is used to find the most similar actor, we've tried increasing the *k* parameter. Not only it do not boost user experience but also adds unwanted ambiguity because single, the most similar photo was no longer available.

After that we've implemented averaging face embedding, which significantly improve stability.

[//]: # (tutaj trzeba wstawić wykresy o których rozmawialiśmy ostatnio)

## Visualizing the results

The embedding produced by `face_recognition` package is **128** dimensional vector. In order to investigate results we've decided to visualize this data after transforming with PCA. Algorithm was trained on all available photos, but only top 50 actors with the most photos are displayed.

One of the first things that can be seen is visible division of the photos into two clusters. After investigation it turns out that they are men and women (which is quite consistent)

> coś o PCA dodać