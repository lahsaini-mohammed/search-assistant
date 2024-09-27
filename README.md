This project implements a WebSearch Agent system using LangGraph. The system is designed to handle complex search questions by utilizing large language models (LLMs). The workflow is orchestrated via an agent-based graph defined in `graph.py`, where each agent performs a specialized task and passes information to the next agent in the pipeline.

## Features

- **Agent-based Search Workflow**: A set of agents (Planner, Selector, Reporter, Reviewer, Router) collaborate to answer research questions.
- **LLM Integration**: Supports multiple LLMs (Gemini, Groq, Ollama) for natural language processing and reasoning.
- **Serper API**: Used for retrieving search engine results.
- **BeautifulSoup**: Used for scraping and parsing the content of selected web pages.
- **Agent Graph**: A directed graph representing the workflow of agents as they process and refine search results.
- **Interactive CLI**: Run the program from the command line, input your research question, and watch the agents work together to provide a final report.

## How It Works

1. **Planner Agent**: Generates a plan to answer the research question.
2. **Selector Agent**: Selects the most relevant search result from a list of search engine results (SERP).
3. **Reporter Agent**: Extracts and compiles a detailed response based on the selected web page.
4. **Reviewer Agent**: Reviews the report, provides feedback, and decides whether to pass the report or route it back to an earlier agent.
5. **Router Agent**: Determines the next agent based on feedback from the Reviewer.
6. **FinalReport Agent**: Compiles the final report once the process passes all reviews.

## Important Notes

- **Rate Limits**: Be aware that if you're using free tiers of Gemini or Groq LLMs, you may hit rate limits.

- **Model Size**: The workflow does not perform well with small LLMs. It is recommended to use LLMs with at least 70 billion parameters for optimal. Smaller models may struggle with complex tasks and multi-step reasoning.

## Installation

To set up the project, follow these steps:

1. Clone the repository:
    ```bash
    git clone https://github.com/lahsaini-mohammed/search-assistant.git
    cd search-assistant
    ```

2. Install the required dependencies:
    ```bash
    pip install -r requirements.txt
    ```

3. Set up API keys:
   - You will need a Serper API key to fetch search engine results. Add it to your environment variables or directly into the code.

4. (Optional) Configure LLMs:
   - The project supports Gemini, Groq, and Ollama models. Ensure you have access to the corresponding API or inference engine for the LLM you want to use.

## Usage

To run the WebSearch Agent:

1. Run the `app.py` file:
    ```bash
    python app.py
    ```

2. You will be prompted to enter your research question. The agents will process the question step-by-step, displaying the actions of each agent in the terminal.

3. Once all agents have completed their tasks, the final report will be displayed.

## Workflow Overview

The workflow is defined in `graph.py`. The system starts with the **Planner Agent** and progresses through various agents until the **FinalReport Agent** is reached. The structure of the agent interactions is represented as a directed graph with conditional paths, allowing flexibility in rerouting based on the feedback.

- The planner defines a search strategy.
- The selector chooses relevant search results.
- The reporter extracts information from the selected source.
- The reviewer checks the quality of the report.
- The router decides the next action based on the review.
- The final report is generated if all conditions are met.

## File Structure

- `app.py`: Main entry point of the application.
- `graph.py`: Defines the workflow of agents and how they interact.
- `agents.py`: Contains the classes for each agent (Planner, Selector, Reporter, Reviewer, Router, FinalReport, EndNode).
- `prompts.py`: Template prompts for each agent to guide their actions.
- `tools/`: Contains the scraper and serper tools.
- `utils/`: Utility functions used across the project.
- `models/`: Contains models for integrating different LLMs.