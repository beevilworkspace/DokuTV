import sys
import json
from dokutv.domain.overlay import FollowOverlayConfig, OVERLAY_I18N
from dokutv.adapters.follow_overlay_template import render_follow_overlay

def run_tests():
    print("Testing FollowOverlayConfig defaults...")
    c = FollowOverlayConfig()
    assert c.formatted_user == "@DeinKanalName", f"Expected @DeinKanalName, got {c.formatted_user}"
    assert c.lang == "de"
    assert c.effective_cta == "Gefällt dir der Content? Lass ein Follow da!"
    assert c.effective_btn == "💜 Kostenlos Folgen"
    assert c.color == "9146FF"

    print("Testing English localization...")
    c_en = FollowOverlayConfig(lang="en")
    assert c_en.effective_cta == "Enjoying the content? Hit the follow button!"
    assert c_en.effective_btn == "💜 Follow for Free"

    print("Testing Custom text override...")
    c_custom = FollowOverlayConfig(cta="Test CTA", btn="Test BTN")
    assert c_custom.effective_cta == "Test CTA"
    assert c_custom.effective_btn == "Test BTN"

    print("Testing Template rendering...")
    html = render_follow_overlay(c_en)
    assert 'lang="en"' in html
    assert '"Enjoying the content? Hit the follow button!"' in html

    print("ALL TESTS PASSED SUCCESSFULLY!")

if __name__ == "__main__":
    run_tests()
