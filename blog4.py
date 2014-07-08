#!/usr/bin/python3

# Copyright 2014, Oliver Nagy <olitheolix@gmail.com>
#
# This script is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This script is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this script. If not, see <http://www.gnu.org/licenses/>.

"""
This script produces some of the OpenGL figures displayed at
https://olitheolix.com.
"""
import numpy as np
import OpenGL.GL as gl
from PyQt4 import QtCore, QtGui, QtOpenGL

class ViewerWidget(QtOpenGL.QGLWidget):
    def __init__(self, parent = None):
        super().__init__(parent)

        # Size of this Qt window.
        self.win_width, self.win_height = 640, 480

        # Place this Qt window in the top left corner.
        self.setGeometry(0, 0, self.win_width, self.win_height)

        # Specify the field of view, aspect ratio, near- and far plane.
        self.fov = 90.0 * np.pi / 180.0
        self.near = 0.5
        self.far = 10.5

    def initializeGL(self):
        """
        Create the graphic buffers and compile the shaders.
        """
        # Create and bind a new VAO (Vertex Array Object).
        self.vertex_array_object = gl.glGenVertexArrays(1)
        gl.glBindVertexArray(self.vertex_array_object)

        # Upload color values (one for each triangle vertex) in RGB format.
        colBuf = gl.glGenBuffers(1)
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, colBuf)
        col = np.array([1,0,0,0,1,0,0,0,1], dtype=np.float32)
        gl.glBufferData(gl.GL_ARRAY_BUFFER, col, gl.GL_STATIC_DRAW)
        gl.glVertexAttribPointer(0, 3, gl.GL_FLOAT, gl.GL_FALSE, 0, None)
        gl.glEnableVertexAttribArray(0)

        # Create and bind GPU buffer for vertex data (the actual data will
        # be uploaded in the paint routine).
        self.vertexBuffer = gl.glGenBuffers(1)
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, self.vertexBuffer)
        gl.glVertexAttribPointer(1, 4, gl.GL_FLOAT, gl.GL_FALSE, 0, None)
        gl.glEnableVertexAttribArray(1)

        # Enable depth-sorting.
        gl.glEnable(gl.GL_DEPTH_TEST)
        gl.glDepthFunc(gl.GL_LESS)

        # Background color.
        gl.glClearColor(0, 0, 0, 0)

        # Compile- and install shader programs.
        self.shaders = self.linkShaders('blog4.vs', 'blog4.fs')
        gl.glUseProgram(self.shaders)
        
    def paintGL(self):
        """
        Paint the OpenGL scene - Qt calls this method automatically.
        """
        # Clear the OpenGL window and bind the VAO.
        gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)

        # Create perspective matrix.
        P = np.zeros((4,4))
        P[0,0] = self.win_height / (self.win_width * np.tan(self.fov / 2))
        P[1,1] = 1 / np.tan(self.fov / 2)
        P[2,2] = (self.far + self.near) / (self.far - self.near)
        P[2,3] = - 2 * self.far * self.near / (self.far - self.near)
        P[3,2] = 1

        # -----------------------------------------------------------------
        # Uncomment the individual sections to reproduce the Blog figures.
        # -----------------------------------------------------------------

        # Camera position- and vectors.
        p = np.array([6, 0, 6])
        r = np.array([1, 0, 0])
        u = np.array([0, 1, 0])
        f = np.array([0, 0, -1])

        # Camera position- and vectors.
        # p = np.array([13, 0, 6])
        # r = np.array([1, 0, -1]) / np.sqrt(2)
        # u = np.array([0, 1, 0])
        # f = np.array([-1, 0, -1]) / np.sqrt(2)

        # Camera position- and vectors in terms of phi and theta.
        # p = np.array([13, 0, 6])
        # phi, theta = np.array([210, 10]) * np.pi / 180
        # r = np.array([-np.cos(phi), 0, np.sin(phi)])
        # f = np.array([np.sin(phi) * np.cos(theta),
        #               np.sin(theta),
        #               np.cos(theta) * np.cos(phi)])
        # u = np.cross(r, f)

        # Create camera matrices.
        C1 = np.eye(4)
        C1[0,:3] = r
        C1[1,:3] = u
        C1[2,:3] = f
        
        C2 = np.eye(4)
        C2[:3,3] = -p
        
        # Define the triangle's vertex positions in world coordinates.
        v_w_1 = [+2.0, -3.0, 2, 1]
        v_w_2 = [+6.0, +3.0, 2, 1]
        v_w_3 = [+10.0, -3.0, 2, 1]

        # Convert the world coordinates into view/camera coordinates.
        v_1 = np.dot(C1, np.dot(C2, v_w_1))
        v_2 = np.dot(C1, np.dot(C2, v_w_2))
        v_3 = np.dot(C1, np.dot(C2, v_w_3))
        
        # Convert vertex positions into normalised device coordinates.
        v_N_1 = np.dot(P, v_1)
        v_N_2 = np.dot(P, v_2)
        v_N_3 = np.dot(P, v_3)

        # Transfer to GPU (concatenate all vertex positions first; most GPU only
        # accept float32).
        v_N = np.concatenate((v_N_1, v_N_2, v_N_3))
        v_N = v_N.astype(np.float32)
        gl.glBufferData(gl.GL_ARRAY_BUFFER, v_N, gl.GL_STATIC_DRAW)

        # Draw the triangle.
        gl.glDrawArrays(gl.GL_TRIANGLES, 0, 3)

    def resizeGL(self, width, height):
        """
        Qt will call this if the viewport size changes.
        """
        gl.glViewport(0, 0, width, height)

    def compileShader(self, fname, shader_type):
        """
        Compile the ``shader_type`` stored in the file ``fname``.
        """
        shader = gl.glCreateShader(shader_type)
        gl.glShaderSource(shader, open(fname).read())
        gl.glCompileShader(shader)
    
        # Check for shader compilation errors.
        result = gl.glGetShaderiv(shader, gl.GL_COMPILE_STATUS)
        if result == 0:
            raise RuntimeError(gl.glGetShaderInfoLog(shader))
        return shader
     
    def linkShaders(self, vertex_shader, fragment_shader):
        """
        Compile- and link the vertex- and fragment shader.
        """
        # Compile the shaders.
        vs = self.compileShader(vertex_shader, gl.GL_VERTEX_SHADER)
        fs = self.compileShader(fragment_shader, gl.GL_FRAGMENT_SHADER)

        # Link shaders into a program.
        program = gl.glCreateProgram()
        gl.glAttachShader(program, vs)
        gl.glAttachShader(program, fs)
        gl.glLinkProgram(program)

        # Check for linking errors.
        result = gl.glGetProgramiv(program, gl.GL_LINK_STATUS)
        if result == 0:
            raise RuntimeError(gl.glGetProgramInfoLog(program))
        return program
    

def main():
    # Boiler plate for Qt application.
    app = QtGui.QApplication(['olitheolix.com: OpenGL Viewer'])
    widget = ViewerWidget()
    widget.show()
    app.exec_()

if __name__ == '__main__':
    main()
