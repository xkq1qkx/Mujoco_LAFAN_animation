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
init_qpos = [0.000014,-0.000190,0.795357,0.999821,0.011052,0.001000,-0.015335,-0.026773,0.078114,0.283308,0.184754,-0.081484,-0.041303,0.060063,-0.161867,-0.472174,0.230419,-0.205530,0.071652,0.012122,0.000179,-0.000434,0.064821,1.598852,-0.045989,1.404461,0.066124,0.094817,0.161620,0.049839,-1.661855,0.035459,1.402454,-0.063490,0.081957,-0.188957]
with mujoco.viewer.launch_passive(m, d) as viewer:
  # Close the viewer automatically after 30 wall-seconds.
  action_flag = False
  flag_just_change = False
  action_name = "g1/jumps1_subject1.csv"
  start = time.time()
  d.qpos = init_qpos
  mujoco.mj_step(m, d)
  while viewer.is_running() and time.time() - start < 180:
    #if not action_flag:
    #   d.qpos = init_qpos
    #   mujoco.mj_step(m, d)
    #gpt_response = interact_with_gpt()
    if action_flag and flag_just_change:
       flag_just_change = False
       action_start_time = time.time()
       now_action_list = read_csv_to_list(action_name)

    with viewer.lock():
      viewer.opt.flags[mujoco.mjtVisFlag.mjVIS_CONTACTPOINT] = int(d.time % 2)

    # Pick up changes to the physics state, apply perturbations, update options from GUI.
    viewer.sync()
    #time.sleep(0.01)
