import re
import streamlit as st

# display the console processing on streamlit UI
class StreamToStreamlit:
    def __init__(self, expander, show_debug=True):
        self.expander = expander
        self.buffer = []
        self.show_debug = show_debug
        self.agent_colors = {
            'Research Agent': 'red',
            'Content Writer': 'green',
            'Content Evaluator': 'blue',
            'Image Editor': 'orange',
            'Content Publisher': 'purple'
        }
        self.workflow_color = 'black'
        self.transaction_color = 'gray'

    def write(self, data):
        # Filter out ANSI escape codes using a regular expression
        cleaned_data = re.sub(r'\x1B\[[0-9;]*[mK]', '', data)

        # Check if the data contains 'task' information
        task_match_object = re.search(r'\"task\"\s*:\s*\"(.*?)\"', cleaned_data, re.IGNORECASE)
        task_match_input = re.search(r'task\s*:\s*([^\n]*)', cleaned_data, re.IGNORECASE)
        task_value = None
        if task_match_object:
            task_value = task_match_object.group(1)
        elif task_match_input:
            task_value = task_match_input.group(1).strip()

        if task_value:
            self.expander.info(":robot_face: " + task_value)

        # Apply specific colors for agents and workflow/transaction
        for agent, color in self.agent_colors.items():
            if agent in cleaned_data:
                cleaned_data = cleaned_data.replace(agent, f":{color}[{agent}]")

        if "Entering new CrewAgentExecutor chain" in cleaned_data:
            cleaned_data = cleaned_data.replace("Entering new CrewAgentExecutor chain",
                                                f":{self.workflow_color}[Entering new CrewAgentExecutor chain]")

        if "Finished chain." in cleaned_data:
            cleaned_data = cleaned_data.replace("Finished chain.", f":{self.workflow_color}[Finished chain.]")

        if "Transaction" in cleaned_data:
            cleaned_data = cleaned_data.replace("Transaction", f":{self.transaction_color}[Transaction]")

        # Optionally show debug information
        if self.show_debug:
            self.buffer.append(cleaned_data)
            if "\n" in data:
                self.expander.markdown(''.join(self.buffer), unsafe_allow_html=True)
                self.buffer = []

    def show_final_result(self, result):
        self.expander.markdown("## Final Output", unsafe_allow_html=True)
        self.expander.markdown(result, unsafe_allow_html=True)
