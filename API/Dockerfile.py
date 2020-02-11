FROM "ubuntu:bionic"
FROM python:3.7.4

#COPY . /retinanet
WORKDIR /retinanet


RUN apt-get update && yes | apt-get upgrade

RUN apt-get install -y git python3-pip
RUN pip3 install --upgrade pip
#RUN apt-get install sudo


#maybe keras 2.3.1
RUN pip3 install scipy
RUN pip install --no-cache-dir tensorflow==1.15
RUN pip3 install -U keras opencv-python
RUN pip3 install matplotlib
RUN pip3 install h5py
RUN pip3 install Flask
RUN pip3 install opencv-python

#RUN pip3 install tensorflow==1.4.0
RUN pip3 install pandas
RUN pip3 install boto3
RUN pip3 install sqlalchemy
RUN pip install flask gunicorn
RUN pip3 install imageai --upgrade
RUN pip install pymssql==2.1.4
#RUN pip install opencv-python
#RUN pip3 install PIL

RUN pip3 install preprocessing

#RUN apt-get update && apt-get install cmake

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
#RUN pip install https://github.com/OlafenwaMoses/ImageAI/releases/download/2.0.1/imageai-2.0.1-py3-none-any.whl
RUN wget https://github.com/OlafenwaMoses/ImageAI/releases/download/1.0/resnet50_coco_best_v2.0.1.h5
#RUN mv /usr/local/lib/python3.7/site-packages/resnet50_coco_best_v2.0.1.h5 /retinanet

#RUN http://developer.download.nvidia.com/compute/cuda/7.5/Prod/local_installers/cuda_7.5.18_linux.run
#RUN
ENTRYPOINT ["python"]

CMD ["gunicorn", "-b", "0.0.0.0:5000", "testapp.py"]
#CMD python ./retinanet/testapp.py
#CMD /bin/bash

