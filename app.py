import asyncio
import shutil
from autogen import ConversableAgent, UserProxyAgent, AssistantAgent, register_function

import autogen
# import cv2
import os
import json
import random
from datetime import datetime

import requests
#TOOLS

#add skills.py to path
import sys
sys.path.append('..')

from skills import generate_and_save_images, current_time, get_cat_fact
import panel as pn 

pn.extension(design="material")

initiate_chat_task_created = False
input_future = None
show_executor = True

# Get the directory of the current script
current_dir = os.path.dirname(os.path.abspath(__file__))


llm_config = autogen.config_list_from_json(os.path.join(current_dir, "OAI_CONFIG_LIST"))
    

class MyConversableAgent(autogen.ConversableAgent):

    async def a_get_human_input(self, prompt: str) -> str:
        global input_future
        global initiate_chat_task_created

        #show the prompt in the chat interface
        #chat_interface.send(prompt, user="System", respond=False)

        # Create a new Future object for this input operation if none exists
        if input_future is None or input_future.done():
            input_future = asyncio.Future()

        # Wait for the callback to set a result on the future
        await input_future

        # Once the result is set, extract the value and reset the future for the next input operation
        input_value = input_future.result()
        input_future = None
        if input_value.lower() == 'exit':
            initiate_chat_task_created = False
        return input_value

#region desc = "TOOLS"
#Tools are imported from skills.py

#region desc = "AGENTS"
# The user proxy agent is used for interacting with the assistant agent
# and executes tool calls.
user_proxy_agent = MyConversableAgent(
    name="user",
    human_input_mode="ALWAYS",
    llm_config=False,
    code_execution_config=False,
    # is_termination_msg=lambda msg: msg.get("content") is not None and "TERMINATE" in msg["content"],
)

function_executor_agent = ConversableAgent(
    name="executor",
    human_input_mode="NEVER",
    llm_config=llm_config,
    code_execution_config={
        "work_dir": "work_dir",
        "use_docker": False,
    },
)

assistant_agent = autogen.AssistantAgent(
    name="assistant",
    description="A helpful bot that can help with a wide range of tasks",
    system_message="You help the user navigate the conversation. You can ask the user for input, provide information, or ask the user to confirm information. You can also provide feedback to the user. Your goal is to help the user get the information they need. You can run and execture code usign python if a task is not clearly achievable using the known agents and tools. These include, image generation, and a clock",
    llm_config=llm_config,
    human_input_mode="NEVER"
)

image_generator = autogen.ConversableAgent(
    name="image_generator",
    description="generates images from a prompt, there is no need to do anything after calling this agent, it will generate the image and save it to the local directory, go back to the user proxy agent when you are done",
    llm_config=llm_config,
    human_input_mode="NEVER"
)

clock_bot = autogen.ConversableAgent(
    name="clock_bot",
    description="a bot that tells the current time",
    llm_config=llm_config,
    human_input_mode="NEVER"
)

cat_fact_bot = autogen.ConversableAgent(
    name="cat_fact_bot",
    description="a bot that tells a cat fact",
    llm_config=llm_config,
    human_input_mode="NEVER"
)

#endregion

#region desc = " Register the tool signature with the assistant agent."
#register the tools
image_generator.register_for_llm(
    name="generate_and_save_images", description="generates images from a prompt"
)(generate_and_save_images)
function_executor_agent.register_for_execution(name="generate_and_save_images")(generate_and_save_images)

clock_bot.register_for_llm(
    name="current_time", description="returns the current time"
)(current_time)
function_executor_agent.register_for_execution(name="current_time")(current_time)

cat_fact_bot.register_for_llm(
    name="get_cat_fact", description="returns a cat fact"
)(get_cat_fact)
function_executor_agent.register_for_execution(name="get_cat_fact")(get_cat_fact)

#endregion
# Group Chat Setup
groupchat = autogen.GroupChat(
    agents=[user_proxy_agent,function_executor_agent, assistant_agent, image_generator, clock_bot, cat_fact_bot],
    messages=[],
    speaker_selection_method="auto",
    max_round=50
)

manager = autogen.GroupChatManager(
    groupchat=groupchat, llm_config= llm_config
)


avatar = {user_proxy_agent.name:"👤", assistant_agent.name:"🤖", function_executor_agent.name:"👨‍💻", image_generator.name:"🖼️", clock_bot.name:"🕒", cat_fact_bot.name:"🐱" }

def print_messages(recipient, messages, sender, config):

    if all(key in messages[-1] for key in ['name']):
        if messages[-1]['name'] == 'user':
            return False, None
        
        if messages[-1]['name'] == 'clock_bot':
             chat_interface.send("Checking the live time", user=messages[-1]['name'], avatar=avatar[messages[-1]['name']], respond=False)
        
        elif messages[-1]['name'] == 'image_generator' and 'IMAGE GENERATED' not in str(messages[-1]['content']):
            chat_interface.send("Generating an image for you. Please wait for a moment.", user=messages[-1]['name'], avatar=avatar[messages[-1]['name']], respond=False)
        elif messages[-1]['name'] == 'executor' and 'IMAGE GENERATED' in str(messages[-1]['content']):
                filename = str(messages[-1]['content']).replace('IMAGE GENERATED: ', '')
                chat_interface.send(pn.pane.Image(filename), user='image_generator', avatar=avatar['image_generator'], respond=False)

        elif messages[-1]['name'] == 'executor':
            if executor_toggle.value:
                chat_interface.send(messages[-1]['content'], user=messages[-1]['name'], avatar=avatar[messages[-1]['name']], respond=False)
            else:
                chat_interface.send("Executor output is currently hidden", user=messages[-1]['name'], avatar=avatar[messages[-1]['name']], respond=False)
        else:
            if 'IMAGE GENERATED' in str(messages[-1]['content']):
                filename = str(messages[-1]['content']).replace('IMAGE GENERATED: ', '')
                chat_interface.send(pn.pane.Image(filename), user=messages[-1]['name'], avatar=avatar[messages[-1]['name']], respond=False)
            else:
                chat_interface.send(messages[-1]['content'], user=messages[-1]['name'], avatar=avatar[messages[-1]['name']], respond=False)

    return False, None


#register all bots as reply
for bot in [user_proxy_agent, function_executor_agent, image_generator, clock_bot]:
    bot.register_reply(
        [autogen.Agent, None],
        reply_func=print_messages,
        config={"callback": None},
    )

async def delayed_initiate_chat(agent, recipient, message):

    global initiate_chat_task_created
    # Indicate that the task has been created
    initiate_chat_task_created = True

    # Wait for 2 seconds
    await asyncio.sleep(2)

    # Now initiate the chat
    await agent.a_initiate_chat(recipient, message=message)

async def continue_chat(agent, recipient, message):

    # Wait for 2 seconds
    await asyncio.sleep(2)

    await agent.a_send(message=message, recipient=recipient)
    return "done"


async def callback(contents: str, user: str, instance: pn.chat.ChatInterface):
    
    global initiate_chat_task_created
    global input_future

    if not initiate_chat_task_created:
        asyncio.create_task(delayed_initiate_chat(user_proxy_agent, manager, contents))

    else:
        if input_future and not input_future.done():
            input_future.set_result(contents)
            if contents.lower() == 'exit':
                instance.widgets[0].disabled = True
        else:
            #asyncio.create_task(continue_chat(user_proxy_agent, manager, contents))
            print("There is currently no input being awaited.")

def reset(instance: pn.chat.ChatInterface, event):
    global initiate_chat_task_created
    manager.clear_agents_history({"content":"clear history"}, groupchat)
    initiate_chat_task_created = False
    instance.widgets[0].disabled = False
    instance.clear()
    instance.send("Hi, what can I do for you?", user="System", respond=False)


executor_toggle = pn.widgets.Switch(name="Enable Feature", value=False)

chat_interface = pn.chat.ChatInterface(
    callback=callback, 
    show_clear=False, 
    show_undo=False, 
    show_button_name=True,
    show_rerun=False,
    button_properties={
        "new": {"callback": reset, "icon":"message-plus"}
    },
    sizing_mode="scale_width",
    widgets=[

        pn.widgets.TextInput(disabled=False,name="Chat"), # Add this line
        pn.Row(pn.Spacer(), pn.widgets.StaticText(name='Executor Output', value='Show'), executor_toggle, width=150,name="Options") ,
    ],
    show_reaction_icons=False,
)
chat_interface.send("Hi, what can I do for you?", user="System", respond=False)

pn.template.FastListTemplate(
    title="Connected Agents",
    main=[chat_interface],
    main_layout=None,
    theme_toggle=False,
).servable()

pn.serve(pn.Column(chat_interface), port=5006)
