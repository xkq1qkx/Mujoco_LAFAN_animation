import time
import mujoco
import mujoco.viewer
import csv

def read_csv_to_list(filename):
    data = []
    with open(filename, 'r', newline='', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            data.append(row)
    return data

# 使用示例
csv_data = read_csv_to_list("g1/jumps1_subject1.csv")  # 替换为你的CSV文件路径
#m = mujoco.MjModel.from_xml_path('./robot_description/g1/g1_29dof_rev_1_0.urdf')
m = mujoco.MjModel.from_xml_path('./unitree_robots/g1/scene_29dof.xml')
d = mujoco.MjData(m)
print("ddff")
init_qpos = [0,0,0.793,1.0,0,0,0]
with mujoco.viewer.launch_passive(m, d) as viewer:
  # Close the viewer automatically after 30 wall-seconds.
  i=0
  start = time.time()
  while viewer.is_running() and time.time() - start < 120:
    #now_qpos = csv_data[i][:7]
    #d.qpos[:7] = init_qpos
    step_start = time.time()
    i = int((step_start - start)*30)
    d.qpos = csv_data[i]
    d.qpos[3]=csv_data[i][6]
    d.qpos[4:7]=csv_data[i][3:6]
    #d.ctrl = csv_data[i][:29]
    
    #print("Initial qpos:", d.qpos)
    # mj_step can be replaced with code that also evaluates
    # a policy and applies a control signal before stepping the physics.
    mujoco.mj_step(m, d)
    #mujoco.mj_forward(m, d)
    #i += 1
    # Example modification of a viewer option: toggle contact points every two seconds.
    with viewer.lock():
      viewer.opt.flags[mujoco.mjtVisFlag.mjVIS_CONTACTPOINT] = int(d.time % 2)

    # Pick up changes to the physics state, apply perturbations, update options from GUI.
    viewer.sync()
    #time.sleep(0.01)

    # Rudimentary time keeping, will drift relative to wall clock.
    time_until_next_step = m.opt.timestep - (time.time() - step_start)
    if time_until_next_step > 0:
      time.sleep(time_until_next_step)