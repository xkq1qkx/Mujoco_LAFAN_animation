import requests
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

def control_robot(action_name,m,d,viewer):
    file_path = "g1/" + action_name+".csv"
    motion_data = read_csv_to_list(file_path)
    start = time.time()
    while viewer.is_running() and time.time() - start < 30:
        #now_qpos = csv_data[i][:7]
        #d.qpos[:7] = init_qpos
        step_start = time.time()
        i = int((step_start - start)*30)
        d.qpos = motion_data[i]
        d.qpos[3]=motion_data[i][6]
        d.qpos[4:7]=motion_data[i][3:6]
        mujoco.mj_step(m, d)
        with viewer.lock():
            viewer.opt.flags[mujoco.mjtVisFlag.mjVIS_CONTACTPOINT] = int(d.time % 2)
        # Pick up changes to the physics state, apply perturbations, update options from GUI.
        viewer.sync()
    return f"The robot have done the {action_name} action"



def get_current_temperature(location):
    """
    This function gets the current temperature for a given location
    by making an API call to a weather service.
    """
    #api_key = ''
    请输入你自己的Open wheather map 的 api_key
    if len(api_key) == 0:
        api_key = input("please input your OpenWeatherMap API key: ")
    base_url = "http://api.openweathermap.org/data/2.5/weather?"
    complete_url = base_url + "q=" + location + "&appid=" + api_key
    try:
        response = requests.get(complete_url)
        data = response.json()
        if "main" in data and "temp" in data["main"]:
            return f"The current temperature in {location} is {data['main']['temp']} Kelvin."
        else:
            return f"Could not retrieve temperature for {location}."
    except requests.exceptions.RequestException as e:
        return f"An error occurred while fetching the temperature: {e}"

def assistant_process_list(brain_output_str,m,d,viewer):
    tool_function_names=["get_current_temperature","control_robot"]
    """
    This function returns a list of processes that the assistant can handle.
    """
    #print("brain_output_str:", brain_output_str)
    brain_output = eval(brain_output_str)
    last_brain_step = brain_output[-1]
    if last_brain_step["role"] != "brain" or "role" not in last_brain_step:
        raise ValueError("The last step must be from the brain and contain a 'role' key.")
    if "END" in last_brain_step and "text_output" in last_brain_step:
        return last_brain_step["text_output"]
    if "tool_calls" in last_brain_step:
        assistant_step = {}
        assistant_step["role"] = "assistant"
        assistant_step["tool_ans"] = last_brain_step["tool_calls"]
        for tool_ans_item in assistant_step["tool_ans"]:
            if tool_ans_item["name"] not in tool_function_names:
                raise ValueError(f"Tool function {tool_ans_item['name']} is not recognized.")
            if tool_ans_item["name"] == "get_current_temperature":
                tool_ans_str = get_current_temperature(tool_ans_item["arguments"]["location"])
                tool_ans_item["result"] = tool_ans_str
            if tool_ans_item["name"] == "control_robot":
                # Here you would implement the logic to control the robot
                # For now, we just return a placeholder message
                tool_ans_item["result"] = control_robot(tool_ans_item["arguments"]["action_name"],m,d,viewer)
        return assistant_step
    else:
        raise ValueError("There is something wrong with the brain output.")
            
        
