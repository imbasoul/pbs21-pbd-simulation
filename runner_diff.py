# test
from render.render import Render
import taichi as ti
from lib.mesh import *
from lib.module import *
from lib.simulator import Simulation


def init_sim(render=None, **kwargs):
    mesh_sphere = Mesh(filename='./obj/sphere.obj', color=[1.0, 0.4, 0.2], rescale=0.1, translation=[0, 0.4, 0])
    mesh_cloth = Mesh(filename='./obj/cloth.obj', color=[0.5, 0.5, 0.5], rescale=0.1, translation=[0.0, 0.8, 0.0])
    mesh_cloth.set_gravity_affected(True)
    mesh_cloth.set_wind_affected(True)
    module = Module()
    module.add_static_objects(mesh_sphere)
    module.add_simulated_objects(mesh_cloth)
    if render is None:
        render = Render({'static_0': mesh_sphere.export_for_render(), 'simulated_0': mesh_cloth.export_for_render()})
    sim = Simulation(module, render, **kwargs)
    return sim



if __name__ == '__main__':
    ti.init()

    # X, Y, Z 对应关系
    # X，Z：平面坐标，X控制水平方向，从左到右依次递增；Z控制竖直方向，从后到前依次递增。（原点在初始视角平面的左上角）
    # Y：纵向坐标
    # rescale：放大缩小使用；translation：尺度变换后，物体的平移
    # !!!!!!! _large物体由open3d导出，其triangle的索引顺序与小文件的相反，会导致平面法向量计算相反，渲染的颜色面出错
    # mesh_sphere = Mesh(filename='./obj/sphere_large.obj', color=[1.0, 0.4, 0.2], translation=[0, 0.6, 0], reverse_triangle_verts=True)
    # mesh_cloth = Mesh(filename='./obj/cloth_large.obj', color=[0.2, 0.2, 0.2], translation=[0, 1.0, 0], reverse_triangle_verts=True)

    # mesh_sphere = Mesh(filename='./obj/sphere.obj', color=[1.0, 0.4, 0.2], rescale=0.1, translation=[0, 0.4, 0])
    # mesh_cloth = Mesh(filename='./obj/cloth.obj', color=[0.5, 0.5, 0.5], rescale=0.2, translation=[0.5, 0.8, 0.3])
    # mesh_cloth.set_gravity_affected(True)
    # mesh_cloth.set_wind_affected(True)
    #
    # module = Module()
    # module.add_static_objects(mesh_sphere)
    # module.add_simulated_objects(mesh_cloth)
    # render = Render({'static_0': mesh_sphere.export_for_render(), 'simulated_0': mesh_cloth.export_for_render()})
    # sim = Simulation(module, render)
    sim = init_sim()
    iter = 10
    for i in range(iter):
        with ti.Tape(sim.loss):
            sim.run()
            sim.compute_loss()
        grad = sim.wind_speed.grad[None]
        sim.optimize()
        # sim.init_episode()
        old_wind_speed = sim.wind_speed
        # print("wind_speed", sim.wind_speed)
        sim = init_sim(render=sim.render, wind_speed=old_wind_speed)
        print("wind_speed", sim.wind_speed)
        # mesh_sphere = Mesh(filename='./obj/sphere.obj', color=[1.0, 0.4, 0.2], rescale=0.1, translation=[0, 0.4, 0])
        # mesh_cloth = Mesh(filename='./obj/cloth.obj', color=[0.5, 0.5, 0.5], rescale=0.2, translation=[0.5, 0.8, 0.3])
        # mesh_cloth.set_gravity_affected(True)
        # mesh_cloth.set_wind_affected(True)
        # module = Module()
        # module.add_static_objects(mesh_sphere)
        # module.add_simulated_objects(mesh_cloth)
        # sim = Simulation(module, render)
        # sim.wind_speed=old_wind_speed
    sim = init_sim(render=sim.render, wind_speed=old_wind_speed, full_sim=True, total_step=999999)
    sim.run()