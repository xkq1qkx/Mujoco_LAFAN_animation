
from openai import OpenAI
import base64
import requests
from assistant_process_list import assistant_process_list, get_current_temperature
from PIL import Image
from termcolor import colored
import time
import mujoco
import mujoco.viewer
import csv

import matplotlib.pyplot as plt

def display_project_icon():
    # Create a detailed robot icon using ASCII art with two colors

    icon = [
       """
  ____         _        _   _             ____       _           _        
 |  _ \ ___   / \   ___| |_(_) ___  _ __ |  _ \ ___ | |__   ___ | |_      
 | |_) / _ \ / _ \ / __| __| |/ _ \| '_ \| |_) / _ \| '_ \ / _ \| __|____ 
 |  _ <  __// ___ \ (__| |_| | (_) | | | |  _ < (_) | |_) | (_) | ||_____|
 |_| \_\___/_/   \_\___|\__|_|\___/|_| |_|_| \_\___/|_.__/ \___/ \__|     
    / \   __ _  ___ _ __ | |_                                             
   / _ \ / _` |/ _ \ '_ \| __|                                            
  / ___ \ (_| |  __/ | | | |_                                             
 /_/   \_\__, |\___|_| |_|\__|                                            
         |___/                                                            
"""
    ]

    # Allow the user to specify colors for the first and remaining lines
    # Print the first 6 lines in the specified first color and the rest in the specified remaining color
    for i, line in enumerate(icon):
      print(colored(line, 'cyan' if i < 6 else 'green'))

# Display the project icon at the start of the program
display_project_icon()

def encode_image(image_path):
  with open(image_path, "rb") as image_file:
    return base64.b64encode(image_file.read()).decode('utf-8')
  
#client = OpenAI(api_key=gpt_key,base_url=f"https://frostsnowjh.com/v1")
#gpt_key=""
# 请填入你自己的 OpenAI gpt_key
client = OpenAI(api_key=gpt_key,base_url=f"https://api.chatanywhere.tech/v1")
TOOLS_DESCRIPTION = """
You are a humanoid robot control brain.You will be given a instruction by user. And you can get help from the assistant.
You have 2 tool functions to let assistant help you get the information or control the robot (information can help you make decisions):
Let me explian the tool functions:
[
    {
        "type": "function",
        "function": {
            "name": "get_current_temperature",
            "description": "Get current temperature at a location.",
            "parameters": {
                "location": {
                    "type": "string",
                    "description": 'The location to get the temperature for, in the format "City name".',
                },    
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "control_robot",
            "description": "Control the robot to perform a specific action.",
            "parameters": {
                "action_name": {
                    "type": "string",
                    "description": 'The action_name to get what action we ask the robot do. Chose from "dance", "fall_and_get_up", "fight", "jump", "run", "sprint","walk".',
                },
            },
        },
    },
]
Your output should be a List describe the task solving progress. And its structure will be like: instruction, thought , tool call(if needed), tool ans, thought(new step thought), tool call(if needed),thought(new step thought)...... until the task is done.
If you call a tool, the assistant will add a "tool ans" object to the list and input the processed list back to you. If you think the task is done, you should append a "END" object to the end of List. If you think the task is not done, you should not add the "END" object.
Your output is a growing List, which means every time you output, you should not delete the previous steps.
An example pipeline is:

### example_1 start
user instruction is: Please control the robot to dance.
your output should be like this:

[
    {
        "role": "user",
        "instruction": "Please control the robot to dance."
    },
    {
        "role": "brain",
        "thought": "I need to control the robot to perform a dance action. So I will use the control_robot tool and I will set the action_name to 'dance'. Then I will wait for the assistant to execute the action and give me the response."
        "tool_calls": [
            {
                "name": "control_robot",
                "arguments": {
                    "action_name": "dance"
                }
            }
        ]
    }
]

Then this output object is processed by the assistant. The new List will be input to you. For example, if the longer list is:

[
    {
        "role": "user",
        "instruction": "Please control the robot to dance."
    },
    {
        "role": "brain",
        "thought": "I need to control the robot to perform a dance action. So I will use the control_robot tool and I will set the action_name to 'dance'. Then I will wait for the assistant to execute the action and give me the response."
        "tool_calls": [
            {
                "name": "control_robot",
                "arguments": {
                    "action_name": "dance"
                }
            }
        ]
    },
    {
        "role": "assistant",
        "tool_ans": [
            {
                "name": "control_robot",
                "arguments": {
                    "action_name": "dance"
                },
                "result": "The robot have done the dance action."
            }
        ]
    }
]
in this case, your next step output should be like this:
[
    {
        "role": "user",
        "instruction": "Please control the robot to dance."
    },
    {
        "role": "brain",
        "thought": "I need to control the robot to perform a dance action. So I will use the control_robot tool and I will set the action_name to 'dance'. Then I will wait for the assistant to execute the action and give me the response."
        "tool_calls": [
            {
                "name": "control_robot",
                "arguments": {
                    "action_name": "dance"
                }
            }
        ]
    },
    {
        "role": "assistant",
        "tool_ans": [
            {
                "name": "control_robot",
                "arguments": {
                    "action_name": "dance"
                },
                "result": "The robot have done the dance action."
            }
        ]
    },
    {
        "role": "brain",
        "thought": "The robot has successfully performed the dance action. And there is nothing to do. I should add a 'END' property.",
        "text_output": "The robot has successfully performed the dance action.",
        "END": "true"
    }
]
when asistant and user see the "END" property, they know the task is done.
### example_1 end

another example pipeline is:
### example_2 start
user instruction is: if the current temperature in Beijing is not above 30 degrees Celsius, control the robot to jump.
your output should be like this:
[
    {
        "role": "user",
        "instruction": "if the current temperature in Beijing is not above 30 degrees Celsius, control the robot to jump."
    },
    {
        "role": "brain",
        "thought": "I need to get the current temperature at Beijing. So I will use the get_current_temperature tool and I will set the location to 'Beijing'. Then I will wait for the asistant to give me the temperature information. If the temperature is not above 30 degrees Celsius, I will control the robot to jump. If the temperature is above 30 degrees Celsius, I will output the temperature and add a 'END' property.",
        "tool_calls": [
            {
                "name": "get_current_temperature",
                "arguments": {
                    "location": "Beijing"
                }
            }
        ]
    }
]
then this output object is processed by the assistant and add "tool ans". If it is like:
[
    {
        "role": "user",
        "instruction": "if the current temperature in Beijing is not above 30 degrees Celsius, control the robot to jump."
    },
    {
        "role": "brain",
        "thought": "I need to get the current temperature at Beijing. So I will use the get_current_temperature tool and I will set the location to 'Beijing'. Then I will wait for the asistant to give me the temperature information. If the temperature is not above 30 degrees Celsius, I will control the robot to jump. If the temperature is above 30 degrees Celsius, I will output the temperature and add a 'END' property.",
        "tool_calls": [
            {
                "name": "get_current_temperature",
                "arguments": {
                    "location": "Beijing"
                }
            }
        ]
    },
    {
        "role": "assistant",
        "tool_ans": [
            {
                "name": "get_current_temperature",
                "arguments": {
                    "location": "Beijing"
                },
                "result": "25 Celsius"
            }
        ]
    }
]

you need to think and output the next step. Like this:
[
    {
        "role": "user",
        "instruction": "if the current temperature in Beijing is not above 30 degrees Celsius, control the robot to jump."
    },
    {
        "role": "brain",
        "thought": "I need to get the current temperature at Beijing. So I will use the get_current_temperature tool and I will set the location to 'Beijing'. Then I will wait for the asistant to give me the temperature information. If the temperature is not above 30 degrees Celsius, I will control the robot to jump. If the temperature is above 30 degrees Celsius, I will output the temperature and add a 'END' property.",
        "tool_calls": [
            {
                "name": "get_current_temperature",
                "arguments": {
                    "location": "Beijing"
                }
            }
        ]
    },
    {
        "role": "assistant",
        "tool_ans": [
            {
                "name": "get_current_temperature",
                "arguments": {
                    "location": "Beijing"
                },
                "result": "25 Celsius"
            }
        ]
    },
    {
        "role": "brain",
        "thought": "The current temperature in Beijing is 25 degrees Celsius, which is not above 30 degrees Celsius. So I will control the robot to jump. I will use the control_robot tool and I will set the action_name to 'jump'. Then I will wait for the assistant to execute the action and give me the response.",
        "tool_calls": [
            {
                "name": "control_robot",
                "arguments": {
                    "action_name": "jump"
                }
            }
        ]
    }
]

Then this output object is processed by the assistant. It is like:
[
    {
        "role": "user",
        "instruction": "if the current temperature in Beijing is not above 30 degrees Celsius, control the robot to jump."
    },
    {
        "role": "brain",
        "thought": "I need to get the current temperature at Beijing. So I will use the get_current_temperature tool and I will set the location to 'Beijing'. Then I will wait for the asistant to give me the temperature information. If the temperature is not above 30 degrees Celsius, I will control the robot to jump. If the temperature is above 30 degrees Celsius, I will output the temperature and add a 'END' property.",
        "tool_calls": [
            {
                "name": "get_current_temperature",
                "arguments": {
                    "location": "Beijing"
                }
            }
        ]
    },
    {
        "role": "assistant",
        "tool_ans": [
            {
                "name": "get_current_temperature",
                "arguments": {
                    "location": "Beijing"
                },
                "result": "25 Celsius"
            }
        ]
    },
    {
        "role": "brain",
        "thought": "The current temperature in Beijing is 25 degrees Celsius, which is not above 30 degrees Celsius. So I will control the robot to jump. I will use the control_robot tool and I will set the action_name to 'jump'. Then I will wait for the assistant to execute the action and give me the response.",
        "tool_calls": [
            {
                "name": "control_robot",
                "arguments": {
                    "action_name": "jump"
                }
            }
        ]
    },
    {
        "role": "assistant",
        "tool_ans": [
            {
                "name": "control_robot",
                "arguments": {
                    "action_name": "jump"
                },
                "result": "The robot have done the jump action."
            }
        ]
    }
]
You will be given this List and you need to think and output the next step. Like this:
[
    {
        "role": "user",
        "instruction": "if the current temperature in Beijing is not above 30 degrees Celsius, control the robot to jump."
    },
    {
        "role": "brain",
        "thought": "I need to get the current temperature at Beijing. So I will use the get_current_temperature tool and I will set the location to 'Beijing'. Then I will wait for the asistant to give me the temperature information. If the temperature is not above 30 degrees Celsius, I will control the robot to jump. If the temperature is above 30 degrees Celsius, I will output the temperature and add a 'END' property.",
        "tool_calls": [
            {
                "name": "get_current_temperature",
                "arguments": {
                    "location": "Beijing"
                }
            }
        ]
    },
    {
        "role": "assistant",
        "tool_ans": [
            {
                "name": "get_current_temperature",
                "arguments": {
                    "location": "Beijing"
                },
                "result": "25 Celsius"
            }
        ]
    },
    {
        "role": "brain",
        "thought": "The current temperature in Beijing is 25 degrees Celsius, which is not above 30 degrees Celsius. So I will control the robot to jump. I will use the control_robot tool and I will set the action_name to 'jump'. Then I will wait for the assistant to execute the action and give me the response.",
        "tool_calls": [
            {
                "name": "control_robot",
                "arguments": {
                    "action_name": "jump"
                }
            }
        ]
    },
    {
        "role": "assistant",
        "tool_ans": [
            {
                "name": "control_robot",
                "arguments": {
                    "action_name": "jump"
                },
                "result": "The robot have done the jump action."
            }
        ]
    },
    {
        "role": "brain",
        "thought": "The robot has successfully performed the jump action. And there is nothing to do. I should add a 'END' property.",
        "text_output": "The current temperature in Beijing is 25 degrees Celsius, which is not above 30. And the robot has successfully performed the jump action.",
        "END": "true"
    }
]

When asistant and user see the "END" property, they know the task is done.
### notice: every time your output will append a new object to the List.
### Now let us start working and see what instruction the user give you.
### every object in the List should have a "role" property, which can be "user", "brain", or "assistant". And the sequence is user -> brain -> assistant -> brain -> assistant -> brain -> assistant ... until the task is done.
"""
user_instruction = input("Please input the user instruction: ")
context_messages=[
  {
    "role":"system",
    "content": TOOLS_DESCRIPTION,
  },
  {
    "role": "user",
    "content": [
        {"type": "text", "text": user_instruction},
    ]
},
]
m = mujoco.MjModel.from_xml_path('./unitree_robots/g1/scene_29dof.xml')
d = mujoco.MjData(m)
with mujoco.viewer.launch_passive(m, d) as viewer:
    for i in range(5):
        response = client.chat.completions.create(
            model="gpt-4o-2024-11-20",
            temperature=0,
            messages=context_messages,
            max_tokens=10000,
            n=1,
            stop=None)
        timly_ans=response.choices[0].message.content
        #print(timly_ans)
        new_list = eval(timly_ans)
        if new_list[-1]["role"] == "brain" and "END" in new_list[-1]:
            print("The task is done.")
            print("Final output:", new_list[-1]["text_output"])
            need_whole_process = input("Do you need to see the whole reasoning process? (yes/no): ")
            if need_whole_process.lower() == "yes":
                print("The whole process is:")
                print(timly_ans)
            break
        assistant_obj = assistant_process_list(timly_ans,m,d,viewer)
        new_list.append(assistant_obj)
        new_list_str = str(new_list)
        context_messages.append({"role":"system","content":timly_ans})
        context_messages.append({"role":"assistant","content":[{"type": "text", "text":new_list_str}]})
'''
    asistant_processed_list="""
[
    {
        "role": "user",
        "instruction": "tell me the current weather in Shanghai."
    },
    {
        "role": "brain",
        "thought": "I need to get the current temperature at Shanghai. So I will use the get_current_temperature tool and I will set the location to 'Shanghai'. Then I will wait for the assistant to provide the temperature information.",
        "tool_calls": [
            {
                "name": "get_current_temperature",
                "arguments": {
                    "location": "Shanghai"
                }
            }
        ]
    },
    {
        "role": "assistant",
        "tool_ans": [
            {
                "name": "get_current_temperature",
                "arguments": {
                    "location": "Shanghai"
                },
                "result": "The current temperature in Shanghai is 25 degrees Celsius."
            }
        ]
    }
]
"""
'''
  #asistant_processed_object = asistant_process_gpt_output_object(timly_ans)

  #context_messages.append({"role":"user","content":[{"type": "text", "text":user_response}]})
  #context_messages.append(ques2)
