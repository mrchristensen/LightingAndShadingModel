""" Modified code from Peter Colling Ridge 
    Original found at http://www.petercollingridge.co.uk/pygame-3d-graphics-tutorial
"""

import pygame, math
import numpy as np
import wireframe as wf
import basicShapes as shape

class WireframeViewer(wf.WireframeGroup):
    """ A group of wireframes which can be displayed on a Pygame screen """
    
    def __init__(self, width, height, name="Wireframe Viewer"):
        self.width = width
        self.height = height
        
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption(name)
        
        self.wireframes = {}
        self.wireframe_colours = {}
        self.object_to_update = []
        
        self.displayNodes = False
        self.displayEdges = True
        self.displayFaces = True
        
        self.perspective = False
        self.eyeX = self.width/2
        self.eyeY = 100
        self.light_color = np.array([1,1,1])
        self.view_vector = np.array([0, 0, -1])        
        self.light_vector = np.array([0, 0, -1])  

        self.background = (10,10,50)
        self.nodeColour = (250,250,250)
        self.nodeRadius = 4
        
        self.control = 0

    def rotation_matrix(self, x, y, z):

        if x != 0:
            rad = np.radians(x)
            return np.array([
                [1, 0, 0, 0],
                [0, np.cos(rad), -np.sin(rad), 0],
                [0, np.sin(rad), np.cos(rad), 0],
                [0, 0, 0, 1]
            ])
        elif y != 0:
            rad = np.radians(y)
            return np.array([
                [np.cos(rad), 0, np.sin(rad), 0],
                [0, 1, 0, 0],
                [-np.sin(rad), 0, np.cos(rad), 0],
                [0, 0, 0, 1]
            ])
        elif z != 0:
            rad = np.radians(z)
            return np.array([
                [np.cos(rad), -np.sin(rad), 0, 0],
                [np.sin(rad), np.cos(rad), 0, 0],
                [0, 0, 1, 0],
                [0, 0, 0, 1]
            ])

        return "error"
    
    def addWireframe(self, name, wireframe):
        self.wireframes[name] = wireframe
        #   If colour is set to None, then wireframe is not displayed
        self.wireframe_colours[name] = (250,250,250)
    
    def addWireframeGroup(self, wireframe_group):
        # Potential danger of overwriting names
        for name, wireframe in wireframe_group.wireframes.items():
            self.addWireframe(name, wireframe)
    
    def display(self):
        self.screen.fill(self.background)

        for name, wireframe in self.wireframes.items():
            nodes = wireframe.nodes
            
            if self.displayFaces:
                for (face, colour) in wireframe.sortedFaces():
                    v1 = (nodes[face[1]] - nodes[face[0]])[:3]
                    v2 = (nodes[face[2]] - nodes[face[0]])[:3]

                    normal = np.cross(v1, v2)
                    normal /= np.linalg.norm(normal)
                    towards_us = np.dot(normal, self.view_vector)

                    # Only draw faces that face us
                    if towards_us > 0:
                        m_ambient = 0.1
                        ambient = self.light_color * (m_ambient * colour)

                        #Todo Your lighting code here
                        #Make note of the self.view_vector and self.light_vector 
                        #Use the Phong model

                        # n = np.array([1., 1., -1.]) / np.sqrt(3)
                        # l = np.array([2., 3., -1.]) / np.sqrt(14)
                        # s = np.array([1., 1., 0.8]) * 0.9
                        # s_amb = np.array([1., 1., 0.8]) * 0.1
                        # v = np.array([0, 0, -1])
                        m_diff = np.array([0.1, 0.2, 0.5])
                        m_spec = np.array([0.5, 0.5, 0.5])
                        m_gls = 4.0

                        # c_diff = np.clip(m_diff * self.light_color * colour * max(np.dot(normal, self.light_vector), 0), 0, 255)
                        c_diff = m_diff * self.light_color * colour * max(np.dot(normal, self.light_vector), 0)
                        # print("c_diff =", np.round(c_diff, 2))

                        reflection_vector = 2 * np.dot(self.light_vector, normal) * normal - self.light_vector
                        # c_spec = np.clip(m_spec * self.light_color * colour * np.power(max(np.dot(self.view_vector, reflection_vector), 0), m_gls), 0, 255)
                        c_spec = m_spec * self.light_color * colour * np.power(max(np.dot(self.view_vector, reflection_vector), 0), m_gls)
                        # print("c_spec =", np.round(c_spec, 2))

                        # c_amb = s_amb * m_amb
                        # print("c_amb =", np.round(c_amb, 2))


                        #Once you have implemented diffuse and specular lighting, you will want to include them here
                        c_total = np.clip(c_diff + ambient + c_spec, 0, 255)
                        print("c_total =", np.round(c_total, 2))
                        light_total = c_total

                        pygame.draw.polygon(self.screen, light_total, [(nodes[node][0], nodes[node][1]) for node in face], 0)

                if self.displayEdges:
                    for (n1, n2) in wireframe.edges:
                        if self.perspective:
                            if wireframe.nodes[n1][2] > -self.perspective and nodes[n2][2] > -self.perspective:
                                z1 = self.perspective / (self.perspective + nodes[n1][2])
                                x1 = self.width/2 + z1*(nodes[n1][0] - self.width/2)
                                y1 = self.height/2 + z1*(nodes[n1][1] - self.height/2)
                    
                                z2 = self.perspective / (self.perspective + nodes[n2][2])
                                x2 = self.width/2 + z2*(nodes[n2][0] - self.width/2)
                                y2 = self.height/2 + z2*(nodes[n2][1] - self.height/2)
                                
                                pygame.draw.aaline(self.screen, colour, (x1, y1), (x2, y2), 1)
                        else:
                            pygame.draw.aaline(self.screen, colour, (nodes[n1][0], nodes[n1][1]), (nodes[n2][0], nodes[n2][1]), 1)

            if self.displayNodes:
                for node in nodes:
                    pygame.draw.circle(self.screen, colour, (int(node[0]), int(node[1])), self.nodeRadius, 0)
        
        pygame.display.flip()

    def keyEvent(self, key):
        
        #Todo: key press impl
        homogeneous_light_vector = np.array([*self.light_vector, 1])
        # print("light vector: ", self.light_vector)

        # Pressing the a or d keys should cause a rotation about the Y axis
        if key == pygame.K_a:  # move left
            self.light_vector = np.matmul(self.rotation_matrix(0, 10., 0), homogeneous_light_vector)[:3]
            print("a is pressed")
        elif key == pygame.K_d:
            self.light_vector = np.matmul(self.rotation_matrix(0, -10., 0), homogeneous_light_vector)[:3]
            print("d is pressed")
        # Pressing the w or s keys should cause a rotation about the X axis
        elif key == pygame.K_w:  # Move forward
            self.light_vector = np.matmul(self.rotation_matrix(-10, 0, 0), homogeneous_light_vector)[:3]
            print("w is pressed")
        elif key == pygame.K_s:  # Move back
            self.light_vector = np.matmul(self.rotation_matrix(10., 0, 0), homogeneous_light_vector)[:3]
            print("s is pressed")
        # Pressing the q or e keys should cause a rotation about the Z axis
        elif key == pygame.K_q:
            self.light_vector = np.matmul(self.rotation_matrix(0, 0, -10.), homogeneous_light_vector)[:3]
            print("q is pressed")
        elif key == pygame.K_e:
            self.light_vector = np.matmul(self.rotation_matrix(0, 0, 10.), homogeneous_light_vector)[:3]
            print("e is pressed")

        return

    def run(self):
        """ Display wireframe on screen and respond to keydown events """
        
        running = True
        key_down = False
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    key_down = event.key
                elif event.type == pygame.KEYUP:
                    key_down = None
            
            if key_down:
                self.keyEvent(key_down)
            
            self.display()
            self.update()
            
        pygame.quit()


resolution = 52
viewer = WireframeViewer(600, 400)
viewer.addWireframe('sphere', shape.Spheroid((300,200, 20), (160,160,160), resolution=resolution))

# Colour ball
faces = viewer.wireframes['sphere'].faces
for i in range(int(resolution/4)):
    for j in range(resolution*2-4):
        f = i*(resolution*4-8) +j
        faces[f][1][1] = 0
        faces[f][1][2] = 0

viewer.displayEdges = False
viewer.run()
