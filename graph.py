import json
from langgraph.graph import StateGraph
from langchain_core.messages import HumanMessage
from agents import (
    PlannerAgent,
    SelectorAgent,
    ReporterAgent,
    ReviewerAgent,
    RouterAgent,
    FinalReportAgent,
    EndNodeAgent
)
from prompts import (
    reviewer_prompt_template, 
    planner_prompt_template, 
    selector_prompt_template, 
    reporter_prompt_template,
    router_prompt_template
)
from tools.google_serper import get_google_serper
from tools.scraper import scrape_website
from state import AgentGraphState, get_agent_graph_state

def create_graph(server=None, model=None, temperature=0):
    graph = StateGraph(AgentGraphState)

    graph.add_node(
        "planner", 
        lambda state: PlannerAgent(
            state=state,
            model=model,
            server=server,
            temperature=temperature
        ).invoke(
            research_question=state["research_question"],
            feedback=lambda: get_agent_graph_state(state=state, state_key="reviewer_latest"),
            prompt=planner_prompt_template
        )
    )

    graph.add_node(
        "selector",
        lambda state: SelectorAgent(
            state=state,
            model=model,
            server=server,
            temperature=temperature
        ).invoke(
            research_question=state["research_question"],
            feedback=lambda: get_agent_graph_state(state=state, state_key="reviewer_latest"),
            # previous_selections=lambda: get_agent_graph_state(state=state, state_key="selector_all"),
            previous_selections=lambda: get_agent_graph_state(state=state, state_key="selector_latest"),
            serp=lambda: get_agent_graph_state(state=state, state_key="serper_latest"),
            prompt=selector_prompt_template,
        )
    )

    graph.add_node(
        "reporter", 
        lambda state: ReporterAgent(
            state=state,
            model=model,
            server=server,
            temperature=temperature
        ).invoke(
            research_question=state["research_question"],
            feedback=lambda: get_agent_graph_state(state=state, state_key="reviewer_latest"),
            previous_reports=lambda: get_agent_graph_state(state=state, state_key="reporter_all"),
            # previous_reports=lambda: get_agent_graph_state(state=state, state_key="reporter_latest"),
            research=lambda: get_agent_graph_state(state=state, state_key="scraper_latest"),
            prompt=reporter_prompt_template
        )
    )

    graph.add_node(
        "reviewer", 
        lambda state: ReviewerAgent(
            state=state,
            model=model,
            server=server,
            temperature=temperature
        ).invoke(
            research_question=state["research_question"],
            feedback=lambda: get_agent_graph_state(state=state, state_key="reviewer_all"),
            # feedback=lambda: get_agent_graph_state(state=state, state_key="reviewer_latest"),
            reporter=lambda: get_agent_graph_state(state=state, state_key="reporter_latest"),
            prompt=reviewer_prompt_template
        )
    )

    graph.add_node(
        "router", 
        lambda state: RouterAgent(
            state=state,
            model=model,
            server=server,
            temperature=temperature
        ).invoke(
            research_question=state["research_question"],
            feedback=lambda: get_agent_graph_state(state=state, state_key="reviewer_latest"),
            prompt=router_prompt_template
        )
    )


    graph.add_node(
        "serper_tool",
        lambda state: get_google_serper(
            state=state,
            plan=lambda: get_agent_graph_state(state=state, state_key="planner_latest")
        )
    )

    graph.add_node(
        "scraper_tool",
        lambda state: scrape_website(
            state=state,
            research=lambda: get_agent_graph_state(state=state, state_key="selector_latest")
        )
    )

    graph.add_node(
        "final_report", 
        lambda state: FinalReportAgent(
            state=state
        ).invoke(
            final_response=lambda: get_agent_graph_state(state=state, state_key="reporter_latest")
        )
    )

    graph.add_node("end", lambda state: EndNodeAgent(state).invoke())

    # Define the edges in the agent graph
    def pass_review(state: AgentGraphState):
        review_list = state["router_response"]
        if review_list:
            review = review_list[-1]
        else:
            review = "No review"

        if review != "No review":
            if isinstance(review, HumanMessage):
                review_content = review.content
            else:
                review_content = review
            
            review_data = json.loads(review_content)
            next_agent = review_data["next_agent"]
        else:
            next_agent = "end"

        return next_agent

    # Add edges to the graph
    graph.set_entry_point("planner")
    graph.set_finish_point("end")
    graph.add_edge("planner", "serper_tool")
    graph.add_edge("serper_tool", "selector")
    graph.add_edge("selector", "scraper_tool")
    graph.add_edge("scraper_tool", "reporter")
    graph.add_edge("reporter", "reviewer")
    graph.add_edge("reviewer", "router")

    graph.add_conditional_edges(
        "router",
        lambda state: pass_review(state=state),
    )

    graph.add_edge("final_report", "end")

    return graph

def compile_workflow(graph):
    workflow = graph.compile()
    return workflow