"""Offline checks of deterministic boundaries, real ToolNode and graph routing."""

import unittest
from unittest.mock import patch

from langchain_core.messages import AIMessage, ToolMessage
from analyst_graph import build_graph
from analyst_tools import calculate_change, compare_metric, get_country_data, web_search


class ScriptedModel:
    """Protocol fixture only; never presented as a real agent demonstration."""
    def __init__(self, responses):
        self.responses = iter(responses)

    def bind_tools(self, tools):
        return self

    def invoke(self, messages):
        return next(self.responses)


def call(name, args, identifier="call-1"):
    return AIMessage(content="", tool_calls=[{"name": name, "args": args, "id": identifier}])


class ExerciseTests(unittest.TestCase):
    def test_retrieval_alias_missing_year(self):
        self.assertEqual(get_country_data.invoke({"country": "US", "year": 2024})["inflation"], 3.0)
        self.assertIn("error", get_country_data.invoke({"country": "Japan", "year": 2030}))

    def test_ranking_spread_and_no_partial_comparison(self):
        result = compare_metric.invoke({"countries": ["US", "Germany", "Japan"], "metric": "gdp_growth", "year": 2024})
        self.assertEqual(result["lowest"], "Germany")
        self.assertEqual(result["spread_percentage_points"], 3.0)
        self.assertIn("error", compare_metric.invoke({"countries": ["US", "China"], "metric": "gdp_growth", "year": 2024}))
        self.assertIn("error", compare_metric.invoke({"countries": ["US"], "metric": "productivity_growth", "year": 2024}))

    def test_change_is_percentage_points(self):
        result = calculate_change.invoke({"country": "US", "metric": "inflation", "start_year": 2023, "end_year": 2024})
        self.assertEqual(result["change_percentage_points"], -1.1)

    def test_missing_search_key(self):
        with patch.dict("os.environ", {"TAVILY_API_KEY": ""}):
            self.assertIn("error", web_search.invoke({"query": "Germany 2024 growth"}))

    def test_real_toolnode_loop_and_validator(self):
        graph = build_graph(ScriptedModel([
            call("get_country_data", {"country": "US", "year": 2024}),
            AIMessage(content="The illustrative practice data lists US inflation at 3.0% in 2024; this is not verified official data.")]))
        config = {"configurable": {"thread_id": "loop"}}
        events = list(graph.stream({"messages": [("user", "US inflation?")]}, config, stream_mode="updates"))
        self.assertEqual([next(iter(event)) for event in events], ["analyst", "tools", "analyst", "validate_answer"])
        state = graph.get_state(config).values
        self.assertTrue(any(isinstance(message, ToolMessage) for message in state["messages"]))
        self.assertTrue(state["validation"]["passed"])

    def test_budget_and_new_turn_reset(self):
        answer = AIMessage(content="The practice data is available from the tool; this is a limited illustrative analysis, not official economic evidence.")
        graph = build_graph(ScriptedModel([
            call("get_country_data", {"country": "US", "year": 2024}), answer,
            call("get_country_data", {"country": "Germany", "year": 2024}, "call-2"), answer]), max_tool_calls=1)
        config = {"configurable": {"thread_id": "budget"}}
        for country in ["US", "Germany"]:
            state = graph.invoke({"messages": [("user", country)]}, config)
            self.assertEqual(state["tool_calls_used"], 1)
        self.assertEqual(sum(isinstance(message, ToolMessage) for message in state["messages"]), 2)

    def test_zero_budget_executes_no_tools(self):
        graph = build_graph(ScriptedModel([AIMessage(content="The tool budget is zero; no dataset was retrieved, so quantitative conclusions are unavailable.")]), max_tool_calls=0)
        state = graph.invoke({"messages": [("user", "US inflation?")]}, {"configurable": {"thread_id": "zero"}})
        self.assertFalse(any(isinstance(message, ToolMessage) for message in state["messages"]))

    def test_oversized_batch_never_executes(self):
        response = call("get_country_data", {"country": "US", "year": 2024})
        response.tool_calls.append({"name": "get_country_data", "args": {"country": "Germany", "year": 2024}, "id": "call-2", "type": "tool_call"})
        graph = build_graph(ScriptedModel([response]), max_tool_calls=1)
        state = graph.invoke({"messages": [("user", "Compare countries")]}, {"configurable": {"thread_id": "batch"}})
        self.assertFalse(any(isinstance(message, ToolMessage) for message in state["messages"]))
        self.assertEqual(state["tool_calls_used"], 0)

    def test_tool_error_returns_to_model(self):
        graph = build_graph(ScriptedModel([
            call("compare_metric", {"countries": ["China"], "metric": "productivity_growth", "year": 2024}),
            AIMessage(content="The requested productivity metric is unsupported by this practice dataset; no numerical comparison can be provided.")]))
        state = graph.invoke({"messages": [("user", "China productivity?")]}, {"configurable": {"thread_id": "error"}})
        result = next(message for message in state["messages"] if isinstance(message, ToolMessage))
        self.assertIn("Unsupported metric", result.content)
        self.assertTrue(state["validation"]["passed"])

    def test_validator_reports_issues(self):
        graph = build_graph(ScriptedModel([AIMessage(content="Done.")]))
        state = graph.invoke({"messages": [("user", "Hello")]}, {"configurable": {"thread_id": "short"}})
        self.assertFalse(state["validation"]["passed"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
