# Unitree Control Agent

## ReActionRobot-Agent
This repository contains the code and resources for controlling Unitree robots. It provides an easy-to-use interface for asking a robot-agent to reason and manage robot behaviors. It works like a "Robot Brain".

## Features

- Simple and intuitive control interface.
- Support for multiple Unitree robot models. (only support unitree-g1, but easy to scale up)
- Real-time feedback and monitoring. (using Mujoco viewer as the monitor)
- First open source robot-agent based on LLM. (expand the "ReAction" into physical world, so we call it **"ReActionRobot"**)
- Primitive actions are defined in LAFAN dataset, and they are retarget to humanoid robots. (run, walk, fight, jump, fall and get up, sprint...)
- Record the Chain-of-Thought of the model and the whole tool calling process.
- Manually designed Agent structure using prompt engineering. (the prompt is saved in "agent_build_prompt.txt")

## Robot primitive Action Demo Videos

Below are demonstration videos showcasing some of LAFAN's retarget actions in Mujoco:
![](https://github.com/user-attachments/assets/dabc25c0-893c-432d-a062-f3c7e373c7b1)
![](https://github.com/user-attachments/assets/6b8a8a2b-f07f-4985-ad9c-de1964990c03) 
![](https://github.com/user-attachments/assets/cb3a9be4-25aa-4f81-ae13-ae2c65d68fbf)

## **QA(Question and Answer) Demo video** *(without Motion, but use weather tools for reasoning)* [click to see the demo in bilibili]
[![](https://i0.hdslb.com/bfs/archive/0b2a8ffb71cac12e502f1029f03cf7976663d03c.jpg)
](https://www.bilibili.com/video/BV1wy7nzRExy/?vd_source=73e512caa65b4b2e190a5832c65c1193)

## **QAM(Question, Answer and Motions) Demo video** *(with Motion and reasoning ability)* [click to see the demo in bilibili]
[![](https://i1.hdslb.com/bfs/archive/fa311c0c570372c22cbb779b67ccf8fa205ed757.jpg)](https://www.bilibili.com/video/BV1gh7pzGE48/?spm_id_from=333.1387.homepage.video_card.click&vd_source=73e512caa65b4b2e190a5832c65c1193)
## Getting Started
1. If you need, you can create a new conda environment:
    ```bash
    conda create -n unitree_control_agent python=3.9
    conda activate unitree_control_agent
    ```
2. Clone the repository:
    ```bash
    git clone https://github.com/xkq1qkx/Unitree-Control-Agent.git
    ```
3. Install dependencies:
    ```bash
    pip install mujoco
    
    ## 还有其他依赖比如request openai 以及设计openweathermap的api调用的库
    ## 但是都很好装，使用pip基本上缺什么就装什么 
    ```
4. Run the example visualization:
    ```bash
    cd Unitree-Control-Agent

    python example_primitive_action.py ## Replay some primitive actions in Mujoco
    python example_gpt_api.py 

    ## If you are using MacOS, use mjpython(automatically installed with Mujoco) rather than python:
    mjpython example_primitive_action.py
    mjpython example_gpt_api.py
    ```


## Contributing

Contributions are welcome! Please open an issue or submit a pull request.

