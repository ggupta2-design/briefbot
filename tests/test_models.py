from datetime import date

import pytest

from briefbot.models import ActionItem, BriefError, BriefInput, RiskItem


def test_models_normalize_text():
    brief = BriefInput(
        title="  Launch Brief  ",
        audience="  Product team ",
        objective=" Ship safely ",
        context=("  Customer request ",),
        decisions=(" Use local files ",),
        risks=(RiskItem(" Schedule risk ", " Garima "),),
        actions=(ActionItem(" Write tests ", " Dev ", date(2026, 9, 8)),),
    )

    assert brief.title == "Launch Brief"
    assert brief.context == ("Customer request",)
    assert brief.risks[0].owner == "Garima"
    assert brief.actions[0].description == "Write tests"


@pytest.mark.parametrize(
    "factory,message",
    [
        (lambda: BriefInput("", "team", "goal"), "title cannot be blank"),
        (lambda: RiskItem("   "), "risk description cannot be blank"),
        (lambda: ActionItem("task", "   "), "action owner cannot be blank"),
    ],
)
def test_models_reject_blank_required_values(factory, message):
    with pytest.raises(BriefError, match=message):
        factory()


def test_models_bound_collection_sizes():
    with pytest.raises(BriefError, match="more than 100"):
        BriefInput(
            "Title",
            "Team",
            "Goal",
            context=tuple(f"item {index}" for index in range(101)),
        )


def test_models_bound_text_sizes():
    with pytest.raises(BriefError, match="200 characters"):
        BriefInput("x" * 201, "Team", "Goal")
