FROM "ubuntu:bionic"
FROM python:3.7.4

WORKDIR /retinanet

RUN apt-get update && yes | apt-get upgrade
RUN apt-get install -y git python3-pip
RUN pip3 install --upgrade pip

RUN pip3 install scipy
RUN pip install --no-cache-dir tensorflow==1.15
RUN pip3 install -U keras opencv-python
RUN pip3 install matplotlib
RUN pip3 install h5py
RUN pip3 install Flask
RUN pip3 install opencv-python

RUN pip3 install pandas
RUN pip3 install boto3
RUN pip3 install sqlalchemy
RUN pip install flask gunicorn
RUN pip3 install imageai --upgrade
RUN pip install pymssql==2.1.4

RUN pip3 install preprocessing

RUN pip3 install --upgrade ipython && \
        pip3 --no-cache-dir install \
                Cython \
                ipykernel \
                jupyter \
                path.py \
                Pillow \
                pygments \
                six \
                sphinx \
                wheel \
                zmq \
                && python -m ipykernel.kernelspec


EXPOSE 5000
RUN wget https://github.com/OlafenwaMoses/ImageAI/releases/download/1.0/resnet50_coco_best_v2.0.1.h5

ENTRYPOINT ["python"]

CMD ["gunicorn", "-b", "0.0.0.0:5000", "app.py"]

