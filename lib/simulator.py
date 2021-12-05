import taichi as ti
from lib.mesh import Vertex
from lib.module import Module
from lib.distance_constrain import *
from lib.bending_constrain import *

@ti.data_oriented
class Simulation(object):

    def __init__(self, module: Module, render):
        self.module = module
        self.solver_iterations = 4
        # self.iteration_field = ti.Vector.field(1, float, self.solver_iterations)
        self.time_step = 0.003
        self.gravity = 0.981
        self.wind_speed = 1.5
        self.velocity_damping = 0.999
        self.stretch_factor = 0.999
        self.bend_factor = 0.3
        self.wireframe = False
        self.render = render
        self._mesh_now = None
        self.constrain_builder = DistanceConstraintsBuilder(mesh=self.module.simulated_objects[0], stiffness_factor=0.8, solver_iterations=self.solver_iterations)
        self.bend_constrain = BendingConstraints(mesh=self.module.simulated_objects[0], bend_factor=0.02, solver_iterations=self.solver_iterations)

    def update(self):
        for mesh in self.module.simulated_objects:
            self._mesh_now = mesh
            self.simulate()
        self.rendering()
        if not self.render.vis.poll_events():
            exit(-1)
        self.render.vis.update_renderer()

    # @ti.func
    def apply_constrain(self):
        for _ in range(self.solver_iterations):
            self.constrain_builder.project()
            self.bend_constrain.project()

    @ti.kernel
    def simulate(self):
        #for mesh in self.module.simulated_objects:
        if self._mesh_now.gravity_affected:
            self._mesh_now.apply_impulse(2.0 * self.time_step * ti.Vector([0.0, -self.gravity, 0.0]))
        if self._mesh_now.wind_affected:
            # TODO apply wind
            pass
        
        for i in ti.grouped(self._mesh_now.velocities):
            self._mesh_now.estimated_vertices[i] = self._mesh_now.vertices[i] + self.time_step * self._mesh_now.velocities[i]

        # avoid parallel solver
        self.apply_constrain()

        self._mesh_now.estimated_vertices[0] = self._mesh_now.vertices[0]
        # TODO setup constrain
        # TODO project constraint
        # update velocities and positions
        for i in ti.grouped(self._mesh_now.velocities):
            self._mesh_now.velocities[i] = (self._mesh_now.estimated_vertices[i] - self._mesh_now.vertices[i]) / self.time_step
            self._mesh_now.velocities[i] = self._mesh_now.velocities[i] * self.velocity_damping
            self._mesh_now.vertices[i] = self._mesh_now.estimated_vertices[i]

        # TODO Update velocities of colliding vertices
    
    def rendering(self):
        for i, mesh in enumerate(self.module.simulated_objects):
            self.render.update({'simulated_{}'.format(i): mesh.export_for_render()})
        for i, mesh in enumerate(self.module.static_objects):
            self.render.update({'static_{}'.format(i): mesh.export_for_render()})