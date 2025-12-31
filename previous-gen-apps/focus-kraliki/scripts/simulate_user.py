import os
import json
import time
from datetime import datetime
from playwright.sync_api import sync_playwright, expect, TimeoutError

# Config
PERSONA_ID = "solo-developer"
RUN_ID = datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + "_" + PERSONA_ID
BASE_DIR = f"simulation-runs/{RUN_ID}"
ONBOARDING_DIR = f"{BASE_DIR}/01_onboarding"

os.makedirs(ONBOARDING_DIR, exist_ok=True)

def save_screenshot(page, name):
    timestamp = int(time.time())
    filename = f"{ONBOARDING_DIR}/{name}_{timestamp}.png"
    page.screenshot(path=filename)
    print(f"Saved screenshot: {filename}")

def run_simulation():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            viewport={"width": 1280, "height": 720},
            user_agent="FocusKraliki-SimulationAgent/1.0"
        )
        page = context.new_page()

        # Mock backend for stability in sandbox
        def handle_api(route):
            url = route.request.url
            print(f"Intercepting: {url}")

            # Don't intercept source files
            if url.endswith(".ts") or url.endswith(".js") or url.endswith(".svelte") or url.endswith(".css"):
                route.continue_()
                return

            if "onboarding/status" in url:
                 route.fulfill(json={"completed": False, "step": 0})
            elif "onboarding/personas" in url:
                 route.fulfill(json={"personas": [
                     {"id": "solo-developer", "name": "Solo Developer", "description": "Code alone, focus deeply"},
                     {"id": "freelancer", "name": "Freelancer", "description": "Bill clients, manage time"},
                     {"id": "explorer", "name": "Explorer", "description": "Just looking around"}
                 ]})
            elif "onboarding/select-persona" in url:
                 route.fulfill(json={"success": True})
            elif "onboarding/privacy-preferences" in url:
                 route.fulfill(json={"success": True})
            elif "onboarding/feature-toggles" in url:
                 route.fulfill(json={"success": True})
            elif "onboarding/complete" in url:
                 route.fulfill(json={"success": True})
            elif "auth/me" in url:
                 route.fulfill(json={"id": "sim-user", "email": "sim@example.com", "name": "Sim User"})
            elif "voice/providers" in url:
                 route.fulfill(json={"providers": {}})
            elif "/api/" in url: # Default mock for other API calls
                 route.fulfill(json={})
            else:
                 route.continue_()

        page.route("**/api/**", handle_api)
        # Route other paths too if needed, e.g. personas endpoint if not prefixed?
        # The client uses /api prefix.

        print(f"Starting simulation run: {RUN_ID}")

        # Step 1: Land on Onboarding
        print("Navigating to /onboarding...")
        page.goto("http://localhost:5173/onboarding")

        # Wait for load
        try:
            page.wait_for_selector("h1", timeout=10000)
        except TimeoutError:
            print("Timeout waiting for page load")

        time.sleep(1)
        save_screenshot(page, "01_land_on_onboarding")

        # Step 2: Select Persona
        print("Selecting Solo Developer persona...")
        try:
            # Wait for personas to load
            page.wait_for_selector("text=Solo Developer", timeout=5000)
            # Click the button container
            page.locator("button").filter(has_text="Solo Developer").click()
            save_screenshot(page, "02_persona_selected")
        except Exception as e:
            print(f"Persona selection failed: {e}")
            save_screenshot(page, "02_persona_fail")

        # Step 3: Privacy
        print("Accepting privacy...")
        try:
             page.wait_for_selector("text=Privacy & Data Controls", timeout=5000)
             # Toggle checkbox by clicking label text
             page.get_by_text("I understand that AI features").click()
             save_screenshot(page, "03_privacy_checked")
             page.get_by_role("button", name="Continue").click()
        except Exception as e:
             print(f"Privacy step failed: {e}")
             save_screenshot(page, "03_privacy_fail")

        # Step 4: Feature Toggles
        print("Configuring feature toggles...")
        try:
            page.wait_for_selector("text=Feature Configuration", timeout=5000)
            save_screenshot(page, "04_feature_toggles")
            page.get_by_role("button", name="Continue").click()
        except Exception as e:
            print(f"Feature toggles failed: {e}")
            save_screenshot(page, "04_feature_fail")

        # Step 5: Complete
        print("Completing onboarding...")
        try:
            page.wait_for_selector("text=You're all set!", timeout=5000)
            save_screenshot(page, "05_complete_screen")
            page.get_by_role("button", name="Go to Dashboard").click()
        except Exception as e:
             print(f"Completion step failed: {e}")
             save_screenshot(page, "05_complete_fail")

        # Step 6: Dashboard Landed
        print("Waiting for dashboard...")
        try:
            page.wait_for_url("**/dashboard", timeout=5000)
            # Mock auth check might be needed again?
            # The mock handle_api persists.
            save_screenshot(page, "06_dashboard_landed")
            print("Onboarding complete!")
        except TimeoutError:
             print("Failed to reach dashboard")
             save_screenshot(page, "06_dashboard_fail")

        browser.close()

if __name__ == "__main__":
    run_simulation()
