Vivaldi Installation Prerequisite
=====================

bashrc configure
--

Add below lines at $HOME/.bashrc
##### Below lines are adding path to library, binary, and Vivaldi  
##### If you already register the path, you do not need to add  
                            
- - -
$vi ~/.bashrc

MPI_HOME=/path/to/mpi  
MPI_LIB=$MPI_HOME/lib  
MPI_BIN=$MPI_HOME/bin  

CUDA_HOME=/path/to/cuda  
CUDA_LIB=$CUDA_HOME/lib64  
CUDA_BIN=$CUDA_HOME/bin  

VIVALDI_HOME=/path/to/vivaldi  
VIVALDI_PATH=$VIVALDI_HOME/src/interactive_mode  
vivaldi_path=$VIVALDI_HOME  

LD_LIBRARY_PATH=$CUDA_LIB:$MPI_LIB:$LD_LIBRARY_PATH  
PATH=$CUDA_BIN:$MPI_BIN:$VIVALDI_PATH:$PATH:  

export CUDA_ROOT=$CUDA_HOME  
export LD_LIBRARY_PATH  
export PATH  
export vivaldi_path  


- - -

CUDA
-------------
link : https://developer.nvidia.com/cuda-downloads

$sudo dpkg -i *NAME_OF_CUDA_PACKAGE*

$sudo apt-get update

$sudo apt-get install cuda

- - -

PyCuda
-------------
$sudo apt-get install python-dev

$tar -xzvf pycuda-2016.1.tar.gz

$cd pycuda-2016.1

$./setup.sh

#### To test the PyCuda

$python pycuda_test.py
- - -


OpenMPI
---------------
$tar -xzvf openmpi-1.10.2.tar.gz

$cd openmpi-1.10.2/build

$./setup.sh

$cd /usr/local

$sudo ln -s openmpi-1.10.2/ openmpi

$cd ~/openmpi-1.10.2/example

$make

#### To test OpenMPI

$ bash ring_c
- - -


mpi4py
----------------
$tar -xzvf mpi4py-2.0.0.tar.gz

$cd mpi4py-2.0.0

$vim mpi.cfg

#### Edit below lines in mpi.cfg
[openmpi]

mpi_dir          	= /usr/local/openmpi

mpicc            	= %(mpi_dir)s/bin/mpicc

mpicxx           	= %(mpi_dir)s/bin/mpicxx

library_dirs     	= %(mpi_dir)s/lib

runtime_library_dirs = %(library_dirs)s

#### end edit

$ python setup.py build

$ python setup.py install

#### To test  mpi4py

$ python mpi4py_test.py
- - -


PI, PyOpenGL
-------------
$sudo apt-get build-dep python-imaging

$sudo apt-get install libjpeg8 libjpeg62-dev libfreetype6 libfreetype6-dev

$sudo pip install Pillow

$sudo pip install PyOpenGL

$sudo apt-get autoremove

$sudo apt-get clean

- - -

PyQT4
---------------
$sudo apt-get install libxml2-dev libxslt1-dev python-dev

$sudo apt-get install python-qt4*

$sudo apt-get install qt4-dev-tools pyqt4-dev-tools

$sudo apt-get autoremove

$sudo apt-get clean

- - -
