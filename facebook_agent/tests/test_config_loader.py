from pathlib import Path

from facebook_agent.agent import config_loader


def test_load_configs(tmp_path: Path):
    base = tmp_path / "facebook_agent"
    (base / "config" / "clients").mkdir(parents=True)

    (base / "config" / "global.json").write_text(
        """
        {"timezone":"Europe/Bucharest","llm":{"provider":"openai","model":"gpt","max_tokens":10,"temperature":0.1},
         "scheduler":{"tick_minutes":30,"tolerance_minutes":15},
         "facebook_mcp":{"command":"echo","args":["ok"]},
         "logging":{"type":"csv","file":"/tmp/log.csv"}}
        """,
        encoding="utf-8",
    )
    (base / "config" / "agents.json").write_text(
        """{"agents":{"a1":{"name":"A","language":"ro","tone":"calm","style_notes":"s","content_mix":"mix","max_chars":200}}}""",
        encoding="utf-8",
    )
    (base / "config" / "clients" / "c1.json").write_text(
        """{
            "client_id":"c1","display_name":"Test","agent_id":"a1",
            "business":{"niche":"n","city":"c","language":"ro"},
            "platforms":{"facebook":{"enabled":true,"page_id":"p1"},"instagram":{"enabled":false,"ig_business_id":null}},
            "schedule":{"timezone":"Europe/Bucharest","slots":[{"id":"s1","days_of_week":[1],"time":"10:00","platforms":["facebook"],"campaign":"camp"}]},
            "campaigns":{"camp":{"objective":"o","notes":"n"}},
            "guardrails":{"max_posts_per_day":1}
        }""",
        encoding="utf-8",
    )

    g = config_loader.load_global_config(base)
    assert g.timezone == "Europe/Bucharest"
    agents = config_loader.load_agents_config(base)
    assert "a1" in agents.agents
    clients = config_loader.load_clients(base)
    assert clients[0].client_id == "c1"

