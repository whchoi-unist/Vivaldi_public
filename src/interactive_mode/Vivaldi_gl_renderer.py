#!/home/freyja/python

# For MPI setting
from mpi4py import MPI
from Vivaldi_misc import *
# mpi init
# set environment variabled
import os, sys
VIVALDI_PATH = os.environ.get('vivaldi_path')
sys.path.append(VIVALDI_PATH+'/src')    
sys.path.append(VIVALDI_PATH+'/src/interactive_mode/Vivaldi_gl_renderer')

import OpenGL
OpenGL.ERROR_CHECKING = False
from OpenGL.GLUT import *
from OpenGL.GLU import *
from OpenGL.GL import *
from OpenGL.arrays import ArrayDatatype as ADT

from Buffer import*
from Viewer import*
import sys, time, math, numpy


print_blue("starting GL")


parent = MPI.Comm.Get_parent()
parent = parent.Merge()
comm = parent
size = comm.Get_size()
rank = comm.Get_rank()
name = MPI.Get_processor_name()


package = {'parent':parent, 'comm':comm, 'size':size, 'rank':rank, 'name':name}


source = comm.recv(source=MPI.ANY_SOURCE,  tag=5)
flag = comm.recv(source=source, tag=5)
GL_Data = comm.recv(source=source, tag=5)
#windowSize = comm.recv(source=source, tag=5)

windowSize = [1024, 1024]
mViewer = Viewer("viewer", windowSize, package)

print_blue("GL : recv from runFunc (VerticsData)")


mViewer.setGLData(GL_Data)
#mViewer.initializeBuffer(vertices)
#mViewer.initializeTubeShader()
#mViewer.initializeCircleShader()

print "init End!"
mViewer.EnterMainLoop()


