from mpi4py import MPI
import OpenGL
OpenGL.ERROR_CHECKING = False
from OpenGL.GLUT import *
from OpenGL.GLU import *
from OpenGL.GL import *
from OpenGL.GLX import *
from OpenGL.arrays import ArrayDatatype as ADT
import OpenGL.arrays.vbo as glvbo
from OpenGL.GL.ARB.geometry_shader4 import *
from OpenGL.GL.EXT.geometry_shader4 import *

import sys, time, math, numpy
from Buffer import*
#from Draw import*


import os, sys
VIVALDI_PATH = os.environ.get('vivaldi_path')
sys.path.append(VIVALDI_PATH+'/src/interactive_mode/Vivaldi_gl_renderer/')	



class Viewer:

	def __init__(self, name, windowSize, mpiPackage):
		self.ScreenWidth = windowSize[0]
		self.ScreenHeight = windowSize[1]

		self.parent = mpiPackage['parent']
		self.comm = mpiPackage['comm']
		self.size = mpiPackage['size']
		self.rank = mpiPackage['rank']
		self.name = mpiPackage['name']

		glutInit(sys.argv)
		glutInitDisplayMode(GLUT_RGBA | GLUT_DOUBLE | GLUT_DEPTH | GLUT_STENCIL)
		glutInitWindowSize(self.ScreenWidth, self.ScreenHeight)
		glutCreateWindow(name)
		glutDisplayFunc(self.handlerDisplay)
		glutReshapeFunc(self.handlerReshape)
		glutIdleFunc(self.handlerIdle)
		self.initializeGL()

	def initializeGL(self):
		glShadeModel(GL_SMOOTH)                 
		glPixelStorei(GL_UNPACK_ALIGNMENT, 4)
		
		glHint(GL_PERSPECTIVE_CORRECTION_HINT, GL_NICEST)
		glHint(GL_LINE_SMOOTH_HINT, GL_NICEST)
		glHint(GL_POLYGON_SMOOTH_HINT, GL_NICEST)

		glEnable(GL_DEPTH_TEST)
		glEnable(GL_LINE_SMOOTH)
		glEnable(GL_POINT_SMOOTH)
		glEnable(GL_LIGHTING)
		glEnable(GL_VERTEX_ARRAY)
		glEnable(GL_COLOR_ARRAY)
		
		
		
		


		#glEnable(GL_TEXTURE_2D)
		glEnable(GL_NORMALIZE) 
		glEnable(GL_CULL_FACE)
		glEnable(GL_COLOR_MATERIAL)
		glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)
		#glEnable(GL_BLEND);
		#glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA);
		
		
		#glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)
		

		glClearColor(0, 0, 0, 0)
		glClearStencil(0)      
		glClearDepth(1.0)     

		self.CameraPosition = [1,1,1]
		self.ModelViewMatrix = [1.,0.,0.,0.,0.,1.,0.,0.,0.,0.,1.,0.,0.,0.,0.,1.]
		self.ProjectionMatrix = [1.,0.,0.,0.,0.,1.,0.,0.,0.,0.,1.,0.,0.,0.,0.,1.]

		self.ModelViewMatrix = numpy.array(self.ModelViewMatrix, dtype=numpy.float32)
		self.ProjectionMatrix = numpy.array(self.ProjectionMatrix, dtype=numpy.float32)

		self.isLeftButtonPressed = 0
		self.isRightButtonPressed = 0
		self.isMiddleButtonPressed = 0
		self.ModelScaleValue= 1.0
		self.SphereRadius = 1.5
		self.RenderingTime = []
		self.ReadStart = -1
		self.RederInfo = []


		fboColor = Create_Color_Buffer(self.ScreenWidth, self.ScreenHeight)
		fboDepth = Create_Depth_Buffer(self.ScreenWidth, self.ScreenHeight)
		self.fboID = Create_FBO(fboColor, fboDepth , 1)
		self.GL_Data = None
		self.VBOIdList = []

	def setGLData(self, gl_data):
		self.GL_Data = gl_data
	
		for data in self.GL_Data:
			vboid, vbosize = self.initializeBuffer(data['vertics'])
			vboid_index, vbosize_index = self.initializeIndexBuffer(data['indices'])
#			vboid_color, vbosize_color = self.initializeColorBuffer(data['colors'])
			self.VBOIdList.append({'primitive':data['primitive'],
								 'VBOPoint': [vboid, vbosize],
								 'VBOIndex':[vboid_index, vbosize_index],
#								 'VBOColor':[vboid_color, vbosize_color],
								 'radius':data['radius']})

		self.initializeTubeShader()
		self.initializeCircleShader()
		self.initializeLineShader()


	def initializeBuffer(self, Vertices):
		
		Vertices = numpy.array(Vertices,dtype=numpy.float32)
		vboId = glvbo.VBO(Vertices)
		vboSize = len(Vertices)/2
				
		return vboId, vboSize
	
	# def initializeColorBuffer(self, colors):
	
	# 	colors = numpy.array(colors,dtype=numpy.float32)
	# 	vboId = glvbo.VBO(colors)
	# 	vboSize = len(colors)
				
	# 	return vboId, vboSize
	

	def initializeIndexBuffer(self, indices):
	
		indices = numpy.array(indices,dtype=numpy.int32)
		vboId = glvbo.VBO(indices, target=GL_ELEMENT_ARRAY_BUFFER)
		vboSize = len(indices)
				
		return vboId, vboSize
	
	

	def initializeLineShader(self):
		VIVALDI_PATH = os.environ.get('vivaldi_path')

		self.Line_Shader = glCreateProgram()
		self.Line_VertexShader = glCreateShader(GL_VERTEX_SHADER)
		self.Line_GeometryShader = glCreateShader(GL_GEOMETRY_SHADER)
		self.Line_FragmentShader = glCreateShader(GL_FRAGMENT_SHADER)
		glProgramParameteri(self.Line_Shader, GL_GEOMETRY_INPUT_TYPE_ARB, GL_LINES)
		glProgramParameteri(self.Line_Shader, GL_GEOMETRY_OUTPUT_TYPE_ARB, GL_TRIANGLES)
		glProgramParameteri(self.Line_Shader, GL_MAX_GEOMETRY_OUTPUT_VERTICES, 1024)

		glAttachShader(self.Line_Shader, self.Line_VertexShader)
		glAttachShader(self.Line_Shader, self.Line_GeometryShader)
		glAttachShader(self.Line_Shader, self.Line_FragmentShader)

		glShaderSource(self.Line_VertexShader, open(VIVALDI_PATH+'/src/interactive_mode/Vivaldi_gl_renderer/Shader/Line.vert', "r"))
		glCompileShader(self.Line_VertexShader)
		print glGetShaderInfoLog(self.Line_VertexShader)

		glShaderSource(self.Line_GeometryShader, open(VIVALDI_PATH+'/src/interactive_mode/Vivaldi_gl_renderer/Shader/Line.geom', "r"))
		glCompileShader(self.Line_GeometryShader)
		print glGetShaderInfoLog(self.Line_GeometryShader)

		glShaderSource(self.Line_FragmentShader, open(VIVALDI_PATH+'/src/interactive_mode/Vivaldi_gl_renderer/Shader/Line.frag', "r"))
		glCompileShader(self.Line_FragmentShader)
		#print glGetShaderInfoLog(self.Circle_FragmentShader)

		glLinkProgram(self.Line_Shader)
		print glGetProgramInfoLog(self.Line_Shader)


	def initializeTubeShader(self):
		VIVALDI_PATH = os.environ.get('vivaldi_path')

		self.Tube_Shader = glCreateProgram()
		self.Tube_VertexShader = glCreateShader(GL_VERTEX_SHADER)
		self.Tube_GeometryShader = glCreateShader(GL_GEOMETRY_SHADER)
		self.Tube_FragmentShader = glCreateShader(GL_FRAGMENT_SHADER)
		glProgramParameteri(self.Tube_Shader, GL_GEOMETRY_INPUT_TYPE_ARB, GL_LINES)
		glProgramParameteri(self.Tube_Shader, GL_GEOMETRY_OUTPUT_TYPE_ARB, GL_TRIANGLES)
		glProgramParameteri(self.Tube_Shader, GL_MAX_GEOMETRY_OUTPUT_VERTICES, 1024)

		glAttachShader(self.Tube_Shader, self.Tube_VertexShader)
		glAttachShader(self.Tube_Shader, self.Tube_GeometryShader)
		glAttachShader(self.Tube_Shader, self.Tube_FragmentShader)

		glShaderSource(self.Tube_VertexShader, open(VIVALDI_PATH+'/src/interactive_mode/Vivaldi_gl_renderer/Shader/Tube.vert', "r"))
		glCompileShader(self.Tube_VertexShader)
		print glGetShaderInfoLog(self.Tube_VertexShader)

		glShaderSource(self.Tube_GeometryShader, open(VIVALDI_PATH+'/src/interactive_mode/Vivaldi_gl_renderer/Shader/Tube.geom', "r"))
		glCompileShader(self.Tube_GeometryShader)
		print glGetShaderInfoLog(self.Tube_GeometryShader)

		glShaderSource(self.Tube_FragmentShader, open(VIVALDI_PATH+'/src/interactive_mode/Vivaldi_gl_renderer/Shader/Tube.frag', "r"))
		glCompileShader(self.Tube_FragmentShader)
		#print glGetShaderInfoLog(self.Tube_FragmentShader)

		glLinkProgram(self.Tube_Shader)
		print glGetProgramInfoLog(self.Tube_Shader)


	def initializeCircleShader(self):
		VIVALDI_PATH = os.environ.get('vivaldi_path')

		self.Circle_Shader = glCreateProgram()
		self.Circle_VertexShader = glCreateShader(GL_VERTEX_SHADER)
		self.Circle_GeometryShader = glCreateShader(GL_GEOMETRY_SHADER)
		self.Circle_FragmentShader = glCreateShader(GL_FRAGMENT_SHADER)
		glProgramParameteri(self.Circle_Shader, GL_GEOMETRY_INPUT_TYPE_ARB, GL_LINES)
		glProgramParameteri(self.Circle_Shader, GL_GEOMETRY_OUTPUT_TYPE_ARB, GL_TRIANGLES)
		glProgramParameteri(self.Circle_Shader, GL_MAX_GEOMETRY_OUTPUT_VERTICES, 1024)

		glAttachShader(self.Circle_Shader, self.Circle_VertexShader)
		glAttachShader(self.Circle_Shader, self.Circle_GeometryShader)
		glAttachShader(self.Circle_Shader, self.Circle_FragmentShader)

		glShaderSource(self.Circle_VertexShader, open(VIVALDI_PATH+'/src/interactive_mode/Vivaldi_gl_renderer/Shader/Circle.vert', "r"))
		glCompileShader(self.Circle_VertexShader)
		print glGetShaderInfoLog(self.Circle_VertexShader)

		glShaderSource(self.Circle_GeometryShader, open(VIVALDI_PATH+'/src/interactive_mode/Vivaldi_gl_renderer/Shader/Circle.geom', "r"))
		glCompileShader(self.Circle_GeometryShader)
		print glGetShaderInfoLog(self.Circle_GeometryShader)

		glShaderSource(self.Circle_FragmentShader, open(VIVALDI_PATH+'/src/interactive_mode/Vivaldi_gl_renderer/Shader/Circle.frag', "r"))
		glCompileShader(self.Circle_FragmentShader)
		#print glGetShaderInfoLog(self.Circle_FragmentShader)

		glLinkProgram(self.Circle_Shader)
		print glGetProgramInfoLog(self.Circle_Shader)


	def renderTubeScene(self, start, size):
		glUseProgram(self.Tube_Shader)

		glDrawArrays(GL_LINE_STRIP, start, size)

		loc = glGetUniformLocation(self.Tube_Shader, "ModelViewMatrix");
		glUniformMatrix4fv(loc, 1, GL_FALSE, self.ModelViewMatrix);
		loc = glGetUniformLocation(self.Tube_Shader, "ProjectionMatrix");
		glUniformMatrix4fv(loc, 1, GL_FALSE, self.ProjectionMatrix);

		LightPos = [0, 0, 0, 1.0]
		LightAmbient = [.1, .1, .1, 1.0]
		LigthDiffuse = [0.4,0.4,0.4,1.0] 
		LightSpecular = [0.1,0.1,0.1,1.0]
		LightAtt = [0.5, 0.0, 0.0, 1.0]
		
		MaterialAmbient = [ 0.2, 0.2, 0.2, 1.0 ]
		MaterialDiffuse = [0.7,0.7,0.7,1.0]
		MaterialSpecular = [0.1,0.1,0.1,1.0]
		MaterialShineness = 10.0
			
		# light
		loc = glGetUniformLocation(self.Tube_Shader, "light_position");
		glUniform4fv(loc, 1, LightPos);
		loc = glGetUniformLocation(self.Tube_Shader, "light_ambient");
		glUniform4fv(loc, 1, LightAmbient);
		loc = glGetUniformLocation(self.Tube_Shader, "light_diffuse");
		glUniform4fv(loc, 1, LigthDiffuse);
		loc = glGetUniformLocation(self.Tube_Shader, "light_specular");
		glUniform4fv(loc, 1, LightSpecular);
		loc = glGetUniformLocation(self.Tube_Shader, "light_att");
		glUniform4fv(loc, 1, LightAtt);
		
		# material
		loc = glGetUniformLocation(self.Tube_Shader, "material_ambient");
		glUniform4fv(loc, 1, MaterialAmbient);
		loc = glGetUniformLocation(self.Tube_Shader, "material_diffuse");
		glUniform4fv(loc, 1, MaterialDiffuse);
		loc = glGetUniformLocation(self.Tube_Shader, "material_specular");
		glUniform4fv(loc, 1, MaterialSpecular);
		loc = glGetUniformLocation(self.Tube_Shader, "material_shineness");
		glUniform1f(loc, MaterialShineness);

		loc = glGetUniformLocation(self.Tube_Shader, "radius");
		glUniform1f(loc, self.SphereRadius);
		
		glUseProgram(0)

	def renderCircleScene(self,start, size):
		
		
		glUseProgram(self.Circle_Shader)

		glDrawArrays(GL_POINTS, start, size)

		loc = glGetUniformLocation(self.Circle_Shader, "ModelViewMatrix");
		glUniformMatrix4fv(loc, 1, GL_FALSE, self.ModelViewMatrix);
		loc = glGetUniformLocation(self.Circle_Shader, "ProjectionMatrix");
		glUniformMatrix4fv(loc, 1, GL_FALSE, self.ProjectionMatrix);

		LightPos = [0, 0, 0, 1.0]
		LightAmbient = [.1, .1, .1, 1.0]
		LigthDiffuse = [0.4,0.4,0.4,1.0] 
		LightSpecular = [0.1,0.1,0.1,1.0]
		LightAtt = [0.5, 0.0, 0.0, 1.0]
		
		MaterialAmbient = [ 0.2, 0.2, 0.2, 1.0 ]
		MaterialDiffuse = [0.7,0.7,0.7,1.0]
		MaterialSpecular = [0.1,0.1,0.1,1.0]
		MaterialShineness = 10.0
			
		# light
		loc = glGetUniformLocation(self.Circle_Shader, "light_position");
		glUniform4fv(loc, 1, LightPos);
		loc = glGetUniformLocation(self.Circle_Shader, "light_ambient");
		glUniform4fv(loc, 1, LightAmbient);
		loc = glGetUniformLocation(self.Circle_Shader, "light_diffuse");
		glUniform4fv(loc, 1, LigthDiffuse);
		loc = glGetUniformLocation(self.Circle_Shader, "light_specular");
		glUniform4fv(loc, 1, LightSpecular);
		loc = glGetUniformLocation(self.Circle_Shader, "light_att");
		glUniform4fv(loc, 1, LightAtt);
		
		# material
		loc = glGetUniformLocation(self.Circle_Shader, "material_ambient");
		glUniform4fv(loc, 1, MaterialAmbient);
		loc = glGetUniformLocation(self.Circle_Shader, "material_diffuse");
		glUniform4fv(loc, 1, MaterialDiffuse);
		loc = glGetUniformLocation(self.Circle_Shader, "material_specular");
		glUniform4fv(loc, 1, MaterialSpecular);
		loc = glGetUniformLocation(self.Circle_Shader, "material_shineness");
		glUniform1f(loc, MaterialShineness);

		loc = glGetUniformLocation(self.Circle_Shader, "radius");
		glUniform1f(loc, self.SphereRadius);
		
		glUseProgram(0)

	def renderLineScene(self,start, size):
		glUseProgram(self.Line_Shader)

		glDrawArrays(GL_LINE_STRIP, start, size)

		loc = glGetUniformLocation(self.Line_Shader, "ModelViewMatrix");
		glUniformMatrix4fv(loc, 1, GL_FALSE, self.ModelViewMatrix);
		loc = glGetUniformLocation(self.Line_Shader, "ProjectionMatrix");
		glUniformMatrix4fv(loc, 1, GL_FALSE, self.ProjectionMatrix);
	
		glUseProgram(0)


	def send_buffer_to_main(self, source):
	 	
		glBindFramebuffer(GL_FRAMEBUFFER, self.fboID)

		Color_Mat = ( GLubyte * (4*self.ScreenWidth*self.ScreenHeight) )(0)
		glReadPixels(0, 0, self.ScreenWidth, self.ScreenHeight, GL_RGBA, GL_UNSIGNED_BYTE, Color_Mat)
		#print len(Color_Mat)
		Color_Mat = numpy.fromstring(Color_Mat, dtype=numpy.uint8).reshape(self.ScreenHeight, self.ScreenWidth, 4).astype(numpy.float32)
		
		#open("colorMat", "wb").write(Color_Mat)

		Depth_Mat = ( GLubyte * (4 * self.ScreenWidth*self.ScreenHeight) )(0)
		glReadPixels(0, 0, self.ScreenWidth, self.ScreenHeight, GL_DEPTH_COMPONENT, GL_FLOAT, Depth_Mat)

		Depth_Mat = numpy.fromstring(Depth_Mat, dtype=numpy.float32).reshape(self.ScreenHeight, self.ScreenWidth)
		
		#open("depthMat", "wb").write(Depth_Mat)

		glBindFramebuffer(GL_FRAMEBUFFER, 0)

		Depth_Mat = (Depth_Mat * 1600 - 800)
		
		self.comm.send(Color_Mat, dest=source, tag=64)
		self.comm.send(Depth_Mat, dest=source, tag=64)

	

	def handlerDisplay(self):
		while not self.comm.Iprobe(source=MPI.ANY_SOURCE, tag=5):
			time.sleep(0.001)

		source = self.comm.recv(source=MPI.ANY_SOURCE, tag=5)
		flag = self.comm.recv(source=source, tag=5)
		mvmtx = self.comm.recv(source=source, tag=5)
		if flag != "send_buffers":
			assert(False) # Only for this
		self.ModelViewMatrix = mvmtx


		glMatrixMode(GL_MODELVIEW)
		glLoadMatrixf(self.ModelViewMatrix)
		glBindFramebuffer(GL_FRAMEBUFFER, self.fboID)
		glClearColor(0.0, 0.0, 0.0, 0.0)
		glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

		
		glPushMatrix()
		for vbo in self.VBOIdList:
			print "p : " + str(vbo['VBOPoint'])
			print "i : " + str(vbo['VBOIndex'])
			vbo['VBOPoint'][0].bind()
			

			self.SphereRadius = vbo['radius']
			glEnableClientState(GL_VERTEX_ARRAY)
			glEnableClientState(GL_COLOR_ARRAY)

	    		if vbo['primitive'] == "tube":
		    		self.SphereRadius = vbo['radius']
				glVertexPointer(4, GL_FLOAT, 32, vbo['VBOPoint'][0])
		    		glColorPointer(4, GL_FLOAT, 32, vbo['VBOPoint'][0]+16)
				self.renderCircleScene(0, vbo['VBOPoint'][1])

				glVertexPointer(4, GL_FLOAT, 32, vbo['VBOPoint'][0])
		    		glColorPointer(4, GL_FLOAT, 32, vbo['VBOPoint'][0]+16)
				self.renderTubeScene(0, vbo['VBOPoint'][1])

			elif vbo['primitive'] == "line":
				glVertexPointer(4, GL_FLOAT, 32, vbo['VBOPoint'][0])
		    		glColorPointer(4, GL_FLOAT, 32, vbo['VBOPoint'][0]+16)
		    		glDisable(GL_LIGHTING)
		    		self.renderLineScene(0, vbo['VBOPoint'][1])
		    		glEnable(GL_LIGHTING)

			elif vbo['primitive'] == "triangle":
				LightAmbient = [.2, .2, .2, 1.0]
				LigthDiffuse = [.7, .7, .7, 1.0] 
				LightSpecular = [1, 1, 1, 1]
				LightPos = [0, 0, 10000, 0]
				glLightfv(GL_LIGHT0, GL_AMBIENT, LightAmbient)
				glLightfv(GL_LIGHT0, GL_DIFFUSE, LigthDiffuse)
				glLightfv(GL_LIGHT0, GL_SPECULAR, LightSpecular)
				glLightfv(GL_LIGHT0, GL_POSITION, LightPos)
				glEnable(GL_LIGHT0)

				glEnable(GL_INDEX_ARRAY)
				vbo['VBOIndex'][0].bind()
				glEnableClientState(GL_INDEX_ARRAY)
		   		glIndexPointer(GL_INT, 12, vbo['VBOIndex'][0])
				glVertexPointer(4, GL_FLOAT, 32, vbo['VBOPoint'][0])
		   		glColorPointer(4, GL_FLOAT, 32, vbo['VBOPoint'][0]+16)
			 	glDrawElements(GL_TRIANGLES, vbo['VBOIndex'][1], GL_UNSIGNED_INT, None);
				glDisableClientState(GL_INDEX_ARRAY);
				glDisable(GL_INDEX_ARRAY)
				vbo['VBOIndex'][0].unbind()

			elif vbo['primitive'] == "cylinder":
		    		self.SphereRadius = vbo['radius']
				glVertexPointer(4, GL_FLOAT, 32, vbo['VBOPoint'][0])
		    		glColorPointer(4, GL_FLOAT, 32, vbo['VBOPoint'][0]+16)
				self.renderTubeScene(0, vbo['VBOPoint'][1])

			glDisableClientState(GL_COLOR_ARRAY);
			glDisableClientState(GL_VERTEX_ARRAY);


			vbo['VBOPoint'][0].unbind()

		glPopMatrix()

		glBindFramebuffer(GL_FRAMEBUFFER, 0);
		
		self.send_buffer_to_main(source)

		glutSwapBuffers()
		return

	def handlerReshape(self, width, height):
		self.ScreenWidth = width
		self.ScreenHeight = height
		glMatrixMode(GL_PROJECTION)
		glLoadIdentity()
		glViewport(0, 0, self.ScreenWidth, self.ScreenHeight)
		glOrtho(-512, 512, -512, 512, -100*self.ScreenHeight, 100*self.ScreenHeight)
		self.ProjectionMatrix = glGetFloatv(GL_PROJECTION_MATRIX, self.ProjectionMatrix);
		

		return

	def handlerIdle(self):
		glutPostRedisplay()
		return

	def EnterMainLoop(self):
		glutMainLoop()
		return
