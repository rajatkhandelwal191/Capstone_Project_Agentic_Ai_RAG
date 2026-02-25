from app.tools.local_tools import get_open_incidents, get_open_service_requests

def run_tool_flow(state):
    text = state.user_input.lower()

    if "request" in text:
        data = get_open_service_requests()
        if not data:
            state.response = "No open service requests found."
            return state

        formatted = "\n".join(
            [
                f"- {r.id} - {r.department} / {r.request_type} ({r.status})"
                for r in data
            ]
        )
        state.response = f"Open service requests:\n{formatted}"
        return state

    data = get_open_incidents()
    if not data:
        state.response = "No open incidents found."
        return state

    formatted = "\n".join(
        [f"- {i.id} - {i.title} ({i.status})" for i in data]
    )

    state.response = f"Open incidents:\n{formatted}"
    return state
