from langgraph.graph import END, START
from multi_agents.graph import SimpleEdge
from multi_agents.graph import MultiAgentGraph

from .nodes import display_images, noir
from .schema import ContextSchema, StateSchema


def get_multi_agent() -> MultiAgentGraph:
    nodes = [
        noir,
        display_images,
    ]

    edges = [
        SimpleEdge(
            source=START,
            target="noir",
        ),
        SimpleEdge(
            source="noir",
            target="display_images",
        ),
        SimpleEdge(
            source="display_images",
            target=END,
        ),
    ]

    multi_agent = MultiAgentGraph(
        state_schema=StateSchema,
        context_schema=ContextSchema,
        nodes=nodes,
        edges=edges,
        with_memory=False,
    )

    multi_agent.compile()
    return multi_agent
