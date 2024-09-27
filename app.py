from graph import create_graph, compile_workflow
from dotenv import load_dotenv
load_dotenv()

# Set up environment variables for LLama, GroQ, or Gemini servers
###################OLLAMA CONFIGURATION###################
# server = 'ollama'
# model = 'llama3.1:latest'
###################GROQ CONFIGURATION###################
# server = 'groq'
# model = 'llama-3.1-70b-versatile'
###################GEMINI CONFIGURATION###################
server = 'gemini'
model = 'gemini-1.5-flash-002'

iterations = 50

print ("Creating graph and compiling workflow...")
graph = create_graph(server=server, model=model)
workflow = compile_workflow(graph)
print ("Graph and workflow created.")


if __name__ == "__main__":

    verbose = False  # set to True for verbose output

    while True:
        query = input("Please enter your research question: ")
        if query.lower() == "exit":
            break

        dict_inputs = {"research_question": query}
        limit = {"recursion_limit": iterations}

        for event in workflow.stream(dict_inputs, limit):
            if verbose:
                # print("\nState Dictionary:", event)
                with open("state_json.json", "w", encoding="utf-8") as f:
                    f.write(str(event) + "\n")
            else:
                print("\n")



    