# **NeMo-Veritas: Chain-of-Verification (CoVe) & NeMo Guardrails LLM Tester**
![ron_nemo_veritas](https://github.com/user-attachments/assets/c65852c5-757d-4a2a-a283-7809474d63c5)
This open-source Python application demonstrates an interactive way to apply various NVIDIA NeMo Guardrails to an LLM. It features a custom implementation of the Chain-of-Verification (CoVe) technique and allows the user to dynamically select and activate a suite of other built-in guardrails at runtime.

This project is intended for Security Engineers, LLM Security Researchers, and developers looking to build more secure and reliable AI applications.

## **Features**

* **Interactive Guardrail Selection:** Choose which guardrails to activate for each session from a command-line menu.  
* **Dynamic Configuration:** The application builds the guardrails configuration on the fly based on your selections.  
* **Chain-of-Verification (CoVe):** A custom action implements the full CoVe pipeline to reduce hallucinations and improve factual accuracy.  
* **Library of Guardrails:** Includes pre-configured rails for:  
  * Jailbreak Detection  
  * Input/Output Content Moderation  
  * Topical Rails (to keep the conversation on specific topics)  
* **LLM Agnostic:** Supports both local LLMs via Ollama and API-based LLMs like OpenAI.

## **How it Works**

1. When you run app.py, it presents a menu of available guardrails defined in the GUARDRAILS\_LIBRARY dictionary.  
2. You select one or more guardrails to activate.  
3. The script loads a base config.yml file.  
4. It then iterates through your selections, dynamically merging the YAML configurations and appending the Colang flow definitions for each chosen guardrail.  
5. If a guardrail requires a custom Python action (like our CoVe implementation), the application imports the necessary module.  
6. Finally, it initializes LLMRails with the complete, dynamically generated configuration and launches the interactive chat.

## **Prerequisites**

* Python 3.9+  
* An Ollama installation (if using a local LLM) or an OpenAI API key.

## **Setup and Installation**

1. **Clone the repository:**  
   git clone \<repository\_url\>  
   cd \<repository\_name\>

2. **Create a virtual environment (recommended):**  
   python \-m venv venv  
   source venv/bin/activate  \# On Windows, use \`venv\\Scripts\\activate\`

3. **Install the dependencies:**  
   pip install \-r requirements.txt

4. **Configure your LLM:**  
   * **For Ollama:**  
     * Make sure the Ollama service is running.  
     * In app.py, set LLM\_PROVIDER \= "ollama".  
     * In cove\_guardrails/config.yml, update the model name if you want to use a specific Ollama model (e.g., llama3).  
   * **For OpenAI:**  
     * Create a .env file in the root of the project:  
       OPENAI\_API\_KEY="your\_openai\_api\_key"

     * In app.py, set LLM\_PROVIDER \= "openai".

## **Running the Application**

Once everything is set up, run the application:

1. python app.py
2. You will first be prompted to select the guardrails you want to activate. After that, you can begin your conversation with the guarded LLM.

## **Future Improvements**

This project has a lot of potential for growth. Here are some ideas for future improvements and contributions:

* **Expand the Guardrails Library:** Integrate more of the [official NeMo Guardrails examples](https://github.com/NVIDIA/NeMo-Guardrails/tree/develop/examples/configs), such as fact-checking against a document (RAG) or detecting sensitive data (PII).  
* **Advanced CoVe:** Enhance the self\_check\_facts action to use external tools or APIs (e.g., a Google Search or Wikipedia API) for more robust verification, rather than relying solely on the LLM's internal knowledge.  
* **Web Interface:** Build a simple web UI using a framework like **Streamlit** or **Flask** to make the application more accessible to non-developers.  
* **Configuration Management:** Allow users to save and load their guardrail selections and configurations.  
* **Enhanced Logging:** Add detailed logging to track which guardrails are triggered and what actions are taken, which is crucial for security auditing.  
* **Support More LLMs:** Add easy configuration options for other popular LLM providers like Anthropic, Cohere, or local models via Hugging Face Transformers.

## **How to Contribute**

Contributions are welcome and appreciated\! If you'd like to contribute, please follow these steps:

1. **Fork the repository** on GitHub.  
2. **Create a new branch** for your feature or bug fix:  
   git checkout \-b feature/your-feature-name

3. **Make your changes** and ensure the code follows a consistent style.  
4. **Test your changes** thoroughly to ensure they don't break existing functionality.  
5. **Submit a pull request** with a clear description of your changes and why they are needed.

## **License**

This project is licensed under the MIT License. See the LICENSE file for more details.

## **Contact**

For questions, issues, or to get involved with the project, please open an issue on the GitHub repository.

**Project Maintainer:** [@gueriila7](https://github.com/gueriila7) | Ron F. Del Rosario | [ronsurf23@gmail.com](mailto:ronsurf23@gmail.com)
