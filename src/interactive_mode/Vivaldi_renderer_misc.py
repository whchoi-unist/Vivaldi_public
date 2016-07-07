from OpenGL.GLUT import *
from OpenGL.GLU import *
from OpenGL.GL import *
from OpenGL.arrays import ArrayDatatype as ADT
import sys, numpy


#from Draw

def drawCube(xRotated, yRotated, zRotated):
    glColor4f(1, 1, 1, 1);
    glRotatef(xRotated*0.5, 1, 0, 0);
    glRotatef(1, 0, 1, 0);
    glRotatef(yRotated*0.7, 0, 0, 1);
    glColor4f(1, 1, 1, 1);
    glBegin(GL_TRIANGLES);
    # front faces
    glNormal3f(0,0,1);
    # face v0-v1-v2
    glTexCoord2f(1,1);  
    glVertex3f(1,1,1);
    glTexCoord2f(0,1);
    glVertex3f(-1,1,1);
    glTexCoord2f(0,0);  
    glVertex3f(-1,-1,1);
    # face v2-v3-v0
    glTexCoord2f(0,0);  
    glVertex3f(-1,-1,1);
    glTexCoord2f(1,0);  
    glVertex3f(1,-1,1);
    glTexCoord2f(1,1);  
    glVertex3f(1,1,1);

    # right faces
    glNormal3f(1,0,0);
    # face v0-v3-v4
    glTexCoord2f(0,1);  
    glVertex3f(1,1,1);
    glTexCoord2f(0,0);  
    glVertex3f(1,-1,1);
    glTexCoord2f(1,0);  
    glVertex3f(1,-1,-1);
    # face v4-v5-v0
    glTexCoord2f(1,0); 
    glVertex3f(1,-1,-1);
    glTexCoord2f(1,1);  
    glVertex3f(1,1,-1);
    glTexCoord2f(0,1);  
    glVertex3f(1,1,1);

    # top faces
    glNormal3f(0,1,0);
    # face v0-v5-v6
    glTexCoord2f(1,0);  
    glVertex3f(1,1,1);
    glTexCoord2f(1,1);  
    glVertex3f(1,1,-1);
    glTexCoord2f(0,1);  
    glVertex3f(-1,1,-1);
    # face v6-v1-v0
    glTexCoord2f(0,1);  
    glVertex3f(-1,1,-1);
    glTexCoord2f(0,0);  
    glVertex3f(-1,1,1);
    glTexCoord2f(1,0);  
    glVertex3f(1,1,1);

    # left faces
    glNormal3f(-1,0,0);
    # face  v1-v6-v7
    glTexCoord2f(1,1);  
    glVertex3f(-1,1,1);
    glTexCoord2f(0,1);  
    glVertex3f(-1,1,-1);
    glTexCoord2f(0,0);  
    glVertex3f(-1,-1,-1);
    # face v7-v2-v1
    glTexCoord2f(0,0);  
    glVertex3f(-1,-1,-1);
    glTexCoord2f(1,0);  
    glVertex3f(-1,-1,1);
    glTexCoord2f(1,1);  
    glVertex3f(-1,1,1);

    # bottom faces
    glNormal3f(0,-1,0);
    # face v7-v4-v3
    glTexCoord2f(0,0);  
    glVertex3f(-1,-1,-1);
    glTexCoord2f(1,0);  
    glVertex3f(1,-1,-1);
    glTexCoord2f(1,1);  
    glVertex3f(1,-1,1);
    # face v3-v2-v7
    glTexCoord2f(1,1);  
    glVertex3f(1,-1,1);
    glTexCoord2f(0,1);  
    glVertex3f(-1,-1,1);
    glTexCoord2f(0,0);  
    glVertex3f(-1,-1,-1);

    # back faces
    glNormal3f(0,0,-1);
    # face v4-v7-v6
    glTexCoord2f(0,0);  
    glVertex3f(1,-1,-1);
    glTexCoord2f(1,0);  
    glVertex3f(-1,-1,-1);
    glTexCoord2f(1,1);  
    glVertex3f(-1,1,-1);
    # face v6-v5-v4
    glTexCoord2f(1,1);  
    glVertex3f(-1,1,-1);
    glTexCoord2f(0,1);  
    glVertex3f(1,1,-1);
    glTexCoord2f(0,0);  
    glVertex3f(1,-1,-1);
    glEnd();
    


def genVertices(points, tags, colorsArr):
    size = len(points)-1
    print size
    vertices = []
    colors = []
    indices = []
    Merge = []
    Index = 0
    colorIndex = 0
    prevTagID = 0
    prevPointID = 0
    
    while Index < size:
        if tags[Index][0] != prevTagID:
            prevTagID = tags[Index][0]
            colorIndex = prevTagID % 15
            
        if prevPointID != points[Index+1][3]:
            prevPointID = points[Index][3]
        else:
            x = float(points[Index][0])
            y = float(points[Index][1])
            z = float(points[Index][2])
            xn = float(points[Index+1][0])
            yn = float(points[Index+1][1])
            zn = float(points[Index+1][2])


            vertices.append(x)
            vertices.append(y)
            vertices.append(z)
            vertices.append(xn)
            vertices.append(yn)
            vertices.append(zn)
            colors.append(colorsArr[colorIndex][0])
            colors.append(colorsArr[colorIndex][1])
            colors.append(colorsArr[colorIndex][2])
            colors.append(colorsArr[colorIndex][0])
            colors.append(colorsArr[colorIndex][1])
            colors.append(colorsArr[colorIndex][2])
  
            Merge.append(x)
            Merge.append(y)
            Merge.append(z)
            Merge.append(colorsArr[colorIndex][0])
            Merge.append(colorsArr[colorIndex][1])
            Merge.append(colorsArr[colorIndex][2])

            Merge.append(xn)
            Merge.append(yn)
            Merge.append(zn)
            Merge.append(colorsArr[colorIndex][0])
            Merge.append(colorsArr[colorIndex][1])
            Merge.append(colorsArr[colorIndex][2])

        Index += 1
    return vertices, colors, Merge

#from Init_Create

def Init_Light():
    lightKa = [.2, .2, .2, 1.0]
    lightKd = [.7, .7, .7, 1.0] 
    lightKs = [1, 1, 1, 1]
    glLightfv(GL_LIGHT0, GL_AMBIENT, lightKa);
    glLightfv(GL_LIGHT0, GL_DIFFUSE, lightKd);
    glLightfv(GL_LIGHT0, GL_SPECULAR, lightKs);
    lightPos = [0, 0, 20, 1]
    glLightfv(GL_LIGHT0, GL_POSITION, lightPos);
    glEnable(GL_LIGHT0); 


def Create_Color_Texture(TEXTURE_WIDTH, TEXTURE_HEIGHT):
	color_tex = glGenTextures(1);
	glBindTexture(GL_TEXTURE_2D, color_tex);
	glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR);
	glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR_MIPMAP_LINEAR);
	glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE);
	glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE);
	glTexParameteri(GL_TEXTURE_2D, GL_GENERATE_MIPMAP, GL_TRUE);
	glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, TEXTURE_WIDTH, TEXTURE_HEIGHT, 0, GL_RGBA, GL_UNSIGNED_BYTE, None);
	glBindTexture(GL_TEXTURE_2D, 0)
	return color_tex

def Create_Depth_Texture(TEXTURE_WIDTH, TEXTURE_HEIGHT):
	depth_tex = glGenTextures(1);
	glBindTexture(GL_TEXTURE_2D, depth_tex);
	glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT);
	glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT);
	glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST);
	glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST);
	glTexParameteri(GL_TEXTURE_2D, GL_DEPTH_TEXTURE_MODE, GL_INTENSITY);
	glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_COMPARE_MODE, GL_COMPARE_R_TO_TEXTURE);
	glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_COMPARE_FUNC, GL_LEQUAL);
	glTexImage2D(GL_TEXTURE_2D, 0, GL_DEPTH_COMPONENT, TEXTURE_WIDTH, TEXTURE_HEIGHT, 0, GL_DEPTH_COMPONENT, GL_FLOAT, None);
	glBindTexture(GL_TEXTURE_2D, 0)
	return depth_tex

def Create_Depth_Buffer(TEXTURE_WIDTH, TEXTURE_HEIGHT):
	depthBuf = glGenRenderbuffers(1);
	glBindRenderbuffer(GL_RENDERBUFFER, depthBuf);
	glRenderbufferStorage(GL_RENDERBUFFER, GL_DEPTH_COMPONENT, TEXTURE_WIDTH, TEXTURE_HEIGHT);
	glBindRenderbuffer(GL_RENDERBUFFER, 0);
	return depthBuf

def Create_Color_Buffer(TEXTURE_WIDTH, TEXTURE_HEIGHT):
	colorBuf = 3	
	print "colorbuffer"
	colorBuf = glGenRenderbuffers(1);
	print "gen"
	glBindRenderbuffer(GL_RENDERBUFFER, colorBuf);
	glRenderbufferStorage(GL_RENDERBUFFER, GL_RGBA, TEXTURE_WIDTH, TEXTURE_HEIGHT);
	glBindRenderbuffer(GL_RENDERBUFFER, 0);
	return colorBuf

def Create_FBO(colorId, depthId, option):
	fboId = glGenFramebuffers(1);
	print "Frame buffer bind!!"
	glBindFramebuffer(GL_FRAMEBUFFER, fboId);    
	if option == 0:
		glFramebufferTexture2D(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT1, GL_TEXTURE_2D, colorId, 0)  
		glFramebufferTexture2D(GL_FRAMEBUFFER, GL_DEPTH_ATTACHMENT, GL_TEXTURE_2D, depthId, 0)
	elif option == 1:
		glFramebufferRenderbuffer(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0, GL_RENDERBUFFER, colorId);
		glFramebufferRenderbuffer(GL_FRAMEBUFFER, GL_DEPTH_ATTACHMENT, GL_RENDERBUFFER, depthId);
	#glFramebufferRenderbuffer(GL_FRAMEBUFFER, GL_DEPTH_ATTACHMENT, GL_RENDERBUFFER, depthBuf);

	status = glCheckFramebufferStatus(GL_FRAMEBUFFER);
	if status == GL_FRAMEBUFFER_COMPLETE:
		print "good"
	glBindFramebuffer(GL_FRAMEBUFFER, 0);
	return fboId


def Create_PBO(TEXTURE_WIDTH, TEXTURE_HEIGHT):
	pboId = glGenBuffers(1);
	glBindBuffer(GL_PIXEL_PACK_BUFFER, pboId);
	glBufferData(GL_PIXEL_PACK_BUFFER, TEXTURE_WIDTH*TEXTURE_HEIGHT*4, None, GL_STREAM_READ);
	glBindBuffer(GL_PIXEL_PACK_BUFFER, 0);
	return pboId


