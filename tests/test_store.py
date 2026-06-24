"""Unit tests for the data spine — no API key needed."""
import pytest
from origami.store import Store, ident_for


@pytest.fixture
def store(tmp_path):
    return Store(tmp_path / "test.db")


def test_add_and_retrieve_campaign(store):
    cid = store.add_campaign("C1 - Agent Devs", "subscription waste")
    camps = store.campaigns()
    assert len(camps) == 1
    assert camps[0]["name"] == "C1 - Agent Devs"


def test_add_person_new(store):
    cid = store.add_campaign("C1")
    status = store.add_person(cid, {
        "name": "Alice Chen", "email": "alice@agentco.io",
        "headline": "AI infra", "company": "AgentCo"
    })
    assert status == "new"
    people = store.people(cid)
    assert len(people) == 1


def test_dedupe(store):
    cid = store.add_campaign("C1")
    p = {"name": "Alice Chen", "email": "alice@agentco.io", "company": "AgentCo"}
    s1 = store.add_person(cid, p)
    s2 = store.add_person(cid, p)
    assert s1 == "new"
    assert s2 == "duplicate"
    assert len(store.people(cid)) == 1


def test_exclusion_suppresses(store):
    cid = store.add_campaign("C1")
    ident = ident_for("bob@example.com")
    store.exclude([ident], "opted_out")
    status = store.add_person(cid, {"name": "Bob", "email": "bob@example.com"})
    assert status == "excluded"
    assert store.people(cid) == []


def test_export_then_reimport_suppressed(store):
    cid = store.add_campaign("C1")
    store.add_person(cid, {"name": "Carol", "email": "carol@ai.io", "company": "AI Corp"})
    store.set_fit(store.people(cid)[0]["id"], "qualified", "perfect fit")
    rows = store.people(cid, status="qualified")
    store.exclude([r["ident"] for r in rows], reason="exported")
    # reimport same lead
    status = store.add_person(cid, {"name": "Carol", "email": "carol@ai.io"})
    assert status == "excluded"
