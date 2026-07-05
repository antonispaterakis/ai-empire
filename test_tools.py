import pytest
from x_research_tool import x_research_tool

def test_x_research_tool():
    result_str = x_research_tool("Test Query")
    assert "trending_topics" in result_str
    assert "Test Query" in result_str
    assert "viral_hooks" in result_str
