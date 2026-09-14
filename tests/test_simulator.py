import pytest
from app.simulator.hidden_rules import HiddenSignalsEngine
from app.simulator.engagement import EngagementSimulator
from app.simulator.audience import AudienceSimulator

def test_hidden_signal_peak_window():
    # Pulse peak window is 17:00-21:00
    peak_signals = HiddenSignalsEngine.calculate_signal_multipliers(
        channel="Pulse", scheduled_time="18:30", format_type="video_script",
        copy="Short copy", cta="Buy now", hashtags=["#coffee"], previous_formats=[],
        content_pillar="Quality", target_audience_keywords=["budget"]
    )
    off_peak_signals = HiddenSignalsEngine.calculate_signal_multipliers(
        channel="Pulse", scheduled_time="08:00", format_type="video_script",
        copy="Short copy", cta="Buy now", hashtags=["#coffee"], previous_formats=[],
        content_pillar="Quality", target_audience_keywords=["budget"]
    )
    assert peak_signals["reach"] > off_peak_signals["reach"]

def test_hidden_signal_question_cta_boost():
    q_signals = HiddenSignalsEngine.calculate_signal_multipliers(
        channel="Forum", scheduled_time="13:00", format_type="Q_and_A",
        copy="What coffee do you drink?", cta="What is your favorite?", hashtags=["#chat"], previous_formats=[],
        content_pillar="Discussion", target_audience_keywords=["coffee"]
    )
    no_q_signals = HiddenSignalsEngine.calculate_signal_multipliers(
        channel="Forum", scheduled_time="13:00", format_type="Q_and_A",
        copy="This coffee is great.", cta="Buy it today.", hashtags=["#chat"], previous_formats=[],
        content_pillar="Discussion", target_audience_keywords=["coffee"]
    )
    assert q_signals["comment_rate"] > no_q_signals["comment_rate"]

def test_hidden_signal_pulse_length_penalty():
    short_pulse = HiddenSignalsEngine.calculate_signal_multipliers(
        channel="Pulse", scheduled_time="18:00", format_type="video_script",
        copy="Short 10 word copy for quick video caption.", cta="Link in bio", hashtags=["#tag"],
        previous_formats=[], content_pillar="Pillar", target_audience_keywords=[]
    )
    long_pulse = HiddenSignalsEngine.calculate_signal_multipliers(
        channel="Pulse", scheduled_time="18:00", format_type="video_script",
        copy=" ".join(["word"] * 85), cta="Link in bio", hashtags=["#tag"],
        previous_formats=[], content_pillar="Pillar", target_audience_keywords=[]
    )
    assert short_pulse["reach"] > long_pulse["reach"]

def test_engagement_simulator_math():
    sim = EngagementSimulator.simulate_post_engagement(
        channel="Pulse", scheduled_time="18:30", format_type="video_script",
        copy="Compact student espresso machine for under $100!", cta="Grab student deal?",
        hashtags=["#coffee", "#dorm"], seed=100
    )
    assert sim["impressions"] > 0
    assert sim["likes"] > 0
    assert sim["comments_count"] >= 1
    assert sim["engagement_rate"] > 0.0

def test_audience_simulator_sensitive_comments():
    comments = AudienceSimulator.generate_comments_for_post(
        channel="Pulse", copy="Espresso machine post", comment_count=5, seed=12
    )
    assert len(comments) > 0
    assert all("author" in c and "content" in c for c in comments)
