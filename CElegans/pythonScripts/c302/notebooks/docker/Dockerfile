FROM jupyter/scipy-notebook:bde52ed89463

RUN mkdir $HOME/env; mkdir $HOME/packages
ENV VENV=$HOME/env/neurosci

ENV NRN_VER=7.4
ENV NRN=nrn-$NRN_VER
ENV PATH=$PATH:$VENV/bin

WORKDIR $HOME/packages
RUN wget http://www.neuron.yale.edu/ftp/neuron/versions/v$NRN_VER/$NRN.tar.gz
RUN tar xzf $NRN.tar.gz; rm $NRN.tar.gz

USER root

RUN apt-get update; apt-get install -y automake libtool build-essential openmpi-bin libopenmpi-dev git vim  \
                       wget libncurses5-dev libreadline-dev libgsl0-dev cython3

USER $NB_USER

RUN mkdir -p $VENV; \
    cd $NRN; mkdir -p $VENV/bin; \
    $HOME/packages/$NRN/configure --with-paranrn --with-nrnpython=/usr/bin/python2 --disable-rx3d --without-iv --prefix=$VENV; \
    make; make install; \
    cd src/nrnpython; /usr/bin/python2 setup.py install; \
    cd $VENV/bin; ln -s ../x86_64/bin/nrnivmodl

USER root
RUN apt-get update && apt-get install -y libxml2-dev libxslt-dev zlib1g-dev openjdk-7-jre xvfb python-pil scrot xserver-xephyr gxmessage python-setuptools libfreetype6-dev python-matplotlib

RUN pip2 install -I airspeed==0.5.4dev-20150515 \
  && pip2 install libneuroml \
  && pip2 install xvfbwrapper \
  && pip2 install pyvirtualdisplay \
  && pip2 install pyneuroml \
  && pip2 install pyscreenshot \
  && pip2 install setuptools \
  && pip2 install rdflib

WORKDIR $HOME/packages

RUN chmod -R 777 /usr/local/

USER $NB_USER

RUN git clone https://github.com/lungd/CElegansNeuroML.git \
    && cd CElegansNeuroML \
    && git checkout docker-notebook \
    && python2 setup.py install

ENV NEURON_HOME=$VENV/x86_64

RUN git clone https://github.com/openworm/PyOpenWorm.git \
  && cd PyOpenWorm && git checkout dev && python2 setup.py install

USER root

RUN chmod -R 777 /usr/local/* && chown -R $NB_USER /usr/local/* && chgrp -R users /usr/local/*

USER $NB_USER
