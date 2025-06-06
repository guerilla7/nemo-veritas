# app.py
# Main application file to run the Chain-of-Verification (CoVe) and other guardrails.

import asyncio
from nemoguardrails import RailsConfig, LLMRails
import os
import yaml
from importlib import import_module

# --- Configuration ---
# You can switch between 'ollama' and 'openai' here.
LLM_PROVIDER = "ollama" 

# --- Guardrails Configuration ---
CONFIG_PATH = os.path.join(os.path.dirname(__file__), "cove_guardrails")

# --- Guardrails Library ---
# This dictionary defines the available guardrails that can be activated.
# Each entry contains:
# - name: A user-friendly name for the menu.
# - config: A dictionary with the YAML configuration for the rail.
# - colang: A string with the Colang flow definitions.
# - actions_path: (Optional) The path to a module containing custom actions.
GUARDRAILS_LIBRARY = {
    "1": {
        "name": "Chain-of-Verification (Custom Fact-Checking)",
        "config": {"rails": {"output": {"flows": ["self check facts"]}}},
        "colang": """
            define user ask question
              "What is the capital of Australia?"
              "Who wrote '1984'?"

            define flow self check facts
              user ask question
              $bot_response = execute llm(query=$last_user_message)
              $fact_check_result = execute self_check_facts(user_message=$last_user_message, bot_message=$bot_response)
              bot $fact_check_result
        """,
        "actions_path": "cove_guardrails.actions"
    },
    "2": {
        "name": "Jailbreak Detection",
        "config": {"rails": {"input": {"flows": ["check for jailbreak"]}}},
        "colang": """
            define flow check for jailbreak
              user said something
              $jailbreak_check = execute self_check_input(type='jailbreak')
              if $jailbreak_check
                bot refuse to respond
        """
    },
    "3": {
        "name": "Input Moderation (Harmful Content)",
        "config": {"rails": {"input": {"flows": ["check input for harmful content"]}}},
        "colang": """
            define flow check input for harmful content
              user said something
              $moderation_check = execute self_check_input(type='moderation')
              if $moderation_check
                bot refuse to respond
        """
    },
    "4": {
        "name": "Output Moderation (Unsafe Content)",
        "config": {"rails": {"output": {"flows": ["check output for unsafe content"]}}},
        "colang": """
            define flow check output for unsafe content
              bot said something
              $unsafe_content_check = execute self_check_output(type='unsafe')
              if $unsafe_content_check
                bot refuse to respond
        """
    },
    "5": {
        "name": "Topical Rails (Politics)",
        "config": {
            "topical_rails": {
                "topics": ["politics"],
                "enabled": True
            }
        },
        "colang": """
            define user express intent on politics
              "What are your thoughts on the recent election?"
              "Tell me about the new government policy."

            define flow
              user express intent on politics
              bot refuse to respond
        """
    }
}

def deep_merge(source, destination):
    """
    A simple deep merge function for dictionaries.
    Merges lists by extending them with unique items.
    """
    for key, value in source.items():
        if isinstance(value, dict):
            node = destination.setdefault(key, {})
            deep_merge(value, node)
        elif isinstance(value, list):
            if key not in destination:
                destination[key] = []
            destination[key].extend(item for item in value if item not in destination[key])
        else:
            destination[key] = value
    return destination

async def main():
    """
    Initializes and runs the LLM with user-selected guardrails.
    """
    # --- Interactive Guardrail Selection ---
    print("Available NeMo Guardrails:")
    for key, value in GUARDRAILS_LIBRARY.items():
        print(f"  {key}: {value['name']}")
    
    choices_str = input("\nEnter the numbers of the guardrails to activate (e.g., 1 3 5), or press Enter for none: ")
    choices = choices_str.split()

    # --- Dynamically Build Configuration ---
    with open(os.path.join(CONFIG_PATH, "config.yml"), 'r') as f:
        config_data = yaml.safe_load(f)

    colang_content = ""
    action_modules = set()
    selected_guardrails_names = []

    for choice in choices:
        if choice in GUARDRAILS_LIBRARY:
            guardrail = GUARDRAILS_LIBRARY[choice]
            selected_guardrails_names.append(guardrail['name'])
            
            # Merge YAML configurations
            config_data = deep_merge(guardrail['config'], config_data)

            # Append Colang content
            colang_content += guardrail['colang'] + "\n\n"

            # Track unique action modules
            if "actions_path" in guardrail:
                action_modules.add(guardrail['actions_path'])
    
    # --- Initialize LLMRails ---
    config = RailsConfig.from_content(
        colang_content=colang_content,
        yaml_content=yaml.dump(config_data)
    )

    # Load and register custom actions if any are specified
    if action_modules:
        for module_path in action_modules:
            import_module(module_path)
            # NeMo Guardrails automatically discovers actions registered with the @action decorator

    app = LLMRails(config)

    # --- Start Interactive Chat ---
    print("\nChain-of-Verification (CoVe) Guardrails Application")
    print("----------------------------------------------------")
    print(f"Using LLM provider: {LLM_PROVIDER}")
    if selected_guardrails_names:
        print("Active Guardrails:")
        for name in selected_guardrails_names:
            print(f"- {name}")
    else:
        print("Active Guardrails: None")
    print("Enter 'exit' to quit the application.\n")

    while True:
        try:
            user_message = input("You: ")
            if user_message.lower() == "exit":
                break

            bot_message = await app.generate_async(messages=[{
                "role": "user",
                "content": user_message
            }])
            print(f"Bot: {bot_message['content']}")

        except Exception as e:
            print(f"An error occurred: {e}")

if __name__ == "__main__":
    asyncio.run(main())

# cove_guardrails/config.yml
# Base NeMo-Guardrails configuration file.
models:
  - type: main
    engine: openai
    model: gpt-3.5-turbo-instruct
  # Specific models for moderation can be added here by the app if needed

colang_version: "2.x"

# The 'rails' and 'topical_rails' sections will be dynamically populated by app.py


# cove_guardrails/actions.py
# Custom actions for the CoVe guardrail.
from nemoguardrails.actions import action
from nemoguardrails.llm.task import LLMTask

@action()
async def self_check_facts(llm, user_message: str, bot_message: str):
    """
    This action performs the Chain-of-Verification (CoVe) process.
    """
    # 1. Plan Verification Questions
    plan_prompt = f"""
    Based on the following user query and bot response, generate a list of questions to verify the factual claims in the response.

    User Query: "{user_message}"
    Bot Response: "{bot_message}"

    Verification Questions:
    """
    verification_questions_str = await llm.execute(task=LLMTask(prompt=plan_prompt))
    verification_questions = [q.strip() for q in verification_questions_str.split("\n") if q.strip() and q.strip().startswith("?")]

    if not verification_questions:
        return bot_message

    # 2. Execute Verifications
    verified_answers = []
    for question in verification_questions:
        answer = await llm.execute(task=LLMTask(prompt=question))
        verified_answers.append(f"Q: {question}\nA: {answer}")
    verified_answers_str = "\n".join(verified_answers)

    # 3. Generate Final Verified Response
    final_response_prompt = f"""
    Based on the original query, the initial response, and the following verification questions and answers, generate a final, verified response.

    Original Query: "{user_message}"
    Initial Response: "{bot_message}"
    
    Verification Q&A:
    {verified_answers_str}

    Final Verified Response:
    """
    final_response = await llm.execute(task=LLMTask(prompt=final_response_prompt))
    return final_response


# requirements.txt
# Python dependencies for the application.
nemoguardrails
ollama
openai
python-dotenv
PyYAML
