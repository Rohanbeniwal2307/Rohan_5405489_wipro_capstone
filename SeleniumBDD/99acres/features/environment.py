import json
import sys
from pathlib import Path

import allure
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from config.config_reader import ConfigReader
from utilities.screenshot import take_screenshot


def _write_allure_metadata():
    results_dir = PROJECT_ROOT / "allure-results"
    results_dir.mkdir(exist_ok=True)

    environment = {
        "Application": "99acres",
        "Framework": "Behave BDD",
        "Module": "New Launch",
        "Base URL": ConfigReader.get("application", "base_url"),
        "Browser": ConfigReader.get("browser", "name", "chrome"),
        "Headless": ConfigReader.get("browser", "headless", "false"),
        "Location": ConfigReader.get("new_launch", "location", "Noida"),
        "Property Type": ConfigReader.get("new_launch", "property_type", "Flat/Apartment"),
        "Budget": (
            f"{ConfigReader.get('new_launch', 'min_budget', '20 Lacs')} - "
            f"{ConfigReader.get('new_launch', 'max_budget', '80 Lacs')}"
        ),
        "Bedroom": ConfigReader.get("new_launch", "bedroom", "2 BHK"),
    }
    (results_dir / "environment.properties").write_text(
        "\n".join(f"{key}={value}" for key, value in environment.items()),
        encoding="utf-8",
    )

    executor = {
        "name": "Local Windows Behave",
        "type": "local",
        "buildName": "99acres New Launch BDD Automation",
        "reportName": "99acres BDD Allure Report",
    }
    (results_dir / "executor.json").write_text(
        json.dumps(executor, indent=2),
        encoding="utf-8",
    )

    categories = [
        {
            "name": "Assertion Failures",
            "matchedStatuses": ["failed"],
            "messageRegex": ".*AssertionError.*",
        },
        {
            "name": "Selenium / UI Failures",
            "matchedStatuses": ["failed", "broken"],
            "traceRegex": ".*selenium.*|.*TimeoutException.*|.*StaleElementReferenceException.*",
        },
        {
            "name": "Product Defects",
            "matchedStatuses": ["failed"],
        },
    ]
    (results_dir / "categories.json").write_text(
        json.dumps(categories, indent=2),
        encoding="utf-8",
    )


def before_all(context):
    context.project_root = PROJECT_ROOT
    _write_allure_metadata()


def before_scenario(context, scenario):
    options = webdriver.ChromeOptions()
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument(f"--window-size={ConfigReader.get('browser', 'window_size', '1920,1080')}")

    if ConfigReader.getboolean("browser", "headless", fallback=False):
        options.add_argument("--headless=new")

    context.driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options,
    )
    context.driver.maximize_window()
    context.driver.set_page_load_timeout(ConfigReader.getint("browser", "page_load_timeout", 60))
    context.driver.execute_cdp_cmd(
        "Page.addScriptToEvaluateOnNewDocument",
        {"source": "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"},
    )
    context.driver.get(ConfigReader.get("application", "base_url"))
    context.start_url = context.driver.current_url
    context.page = None
    context.opened_project = None


def after_step(context, step):
    if step.status == "failed" and hasattr(context, "driver"):
        try:
            screenshot = context.driver.get_screenshot_as_png()
            allure.attach(
                screenshot,
                name=f"{step.name}_failed",
                attachment_type=allure.attachment_type.PNG,
            )
        except Exception:
            pass


def after_scenario(context, scenario):
    if hasattr(context, "driver"):
        try:
            take_screenshot(context.driver, scenario.name)
            allure.attach(
                context.driver.get_screenshot_as_png(),
                name=f"{scenario.name}_{scenario.status.name.lower()}",
                attachment_type=allure.attachment_type.PNG,
            )
        except Exception:
            pass
        try:
            context.driver.quit()
        except Exception:
            pass
