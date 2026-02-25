from app.tools.local_tools import get_open_incidents, get_open_service_requests
from app.core.logger import logger
import time

def run_tool_flow(state):
    request_id = getattr(state, "request_id", None) or "no-request-id"
    text = state.user_input.lower()
    logger.info("request_id=%s | agent=tool_flow | start | text=%s", request_id, text)
    start = time.perf_counter()

    if "request" in text:
        logger.info(
            "request_id=%s | agent=tool_flow | selected_tool=get_open_service_requests",
            request_id,
        )
        data = get_open_service_requests()
        if not data:
            state.response = "No open service requests found."
            elapsed_ms = (time.perf_counter() - start) * 1000.0
            logger.info(
                "request_id=%s | agent=tool_flow | done | result=none | elapsed_ms=%.2f",
                request_id,
                elapsed_ms,
            )
            return state

        formatted = "\n".join(
            [
                f"- {r.id} - {r.department} / {r.request_type} ({r.status})"
                for r in data
            ]
        )
        state.response = f"Open service requests:\n{formatted}"
        elapsed_ms = (time.perf_counter() - start) * 1000.0
        logger.info(
            "request_id=%s | agent=tool_flow | done | tool=get_open_service_requests | result_count=%s | sample_ids=%s | elapsed_ms=%.2f",
            request_id,
            len(data),
            [r.id for r in data[:3]],
            elapsed_ms,
        )
        return state

    logger.info(
        "request_id=%s | agent=tool_flow | selected_tool=get_open_incidents",
        request_id,
    )
    data = get_open_incidents()
    if not data:
        state.response = "No open incidents found."
        elapsed_ms = (time.perf_counter() - start) * 1000.0
        logger.info(
            "request_id=%s | agent=tool_flow | done | result=none | elapsed_ms=%.2f",
            request_id,
            elapsed_ms,
        )
        return state

    formatted = "\n".join(
        [f"- {i.id} - {i.title} ({i.status})" for i in data]
    )

    state.response = f"Open incidents:\n{formatted}"
    elapsed_ms = (time.perf_counter() - start) * 1000.0
    logger.info(
        "request_id=%s | agent=tool_flow | done | tool=get_open_incidents | result_count=%s | sample_ids=%s | elapsed_ms=%.2f",
        request_id,
        len(data),
        [i.id for i in data[:3]],
        elapsed_ms,
    )
    return state
