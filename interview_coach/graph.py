"""LangGraph 图 - 合并 input 到 master"""
"""LangGraph 图 - 合并 input 到 master"""
import re
from langgraph.graph import StateGraph, START, END
from state import InterviewState
from master import (
    master_node,
    route_after_master,
    parse_user_input,
    read_resume_file,
    extract_job_title,
)


def show_result_node(state):
    messages = state.get("messages", [])
    result = state.get("function_result", "")
    new_msg = {
        "role": "assistant",
        "content": f"✅ 完成！\n\n{result}\n\n---\n\n还要别的功能吗？输入 1-8 选择。"
    }
    return {
        "messages": messages + [new_msg],
        "selected_function": None,
    }


def route_after_master(state):
    if not state.get("resume_text"):
        return END
    if not state.get("jd_text"):
        return END
    if not state.get("selected_function"):
        return END
    print(f"[DEBUG route] selected_function={state.get('selected_function')}, next={state.get('next_step')}")
    return state.get("next_step", "show_result")


def build_graph():
    from agents import rewrite, review, predict, risk, intro, company, post, negotiation

    AGENT_MAP = {
        "1": ("subagent_1", rewrite.call_rewrite_agent),
        "2": ("subagent_2", review.call_review_agent),
        "3": ("subagent_3", predict.call_predict_agent),
        "4": ("subagent_4", risk.call_risk_agent),
        "5": ("subagent_5", intro.call_intro_agent),
        "6": ("subagent_6", company.call_company_agent),
        "7": ("subagent_7", post.call_post_agent),
        "8": ("subagent_8", negotiation.call_negotiation_agent),
    }

    builder = StateGraph(InterviewState)

    builder.add_node("master", master_node)
    builder.add_node("show_result", show_result_node)
    for name, func in AGENT_MAP.values():
        builder.add_node(name, func)

    builder.add_edge(START, "master")
    builder.add_conditional_edges(
        "master", route_after_master,
        {END: END, "show_result": "show_result"} | {n: n for n, _ in AGENT_MAP.values()},
    )
    for name, _ in AGENT_MAP.values():
        builder.add_edge(name, "show_result")
    builder.add_edge("show_result", END)

    return builder.compile()


graph = build_graph()