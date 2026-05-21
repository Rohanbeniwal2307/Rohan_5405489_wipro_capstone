import pytest
import allure
import json
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from pathlib import Path

from config.config_reader import ConfigReader


def _get_allure_results_dir(config):
    report_dir = getattr(config.option, "allure_report_dir", None)
    if isinstance(report_dir, list):
        report_dir = report_dir[0] if report_dir else None
    return Path(report_dir or "allure-results")


def pytest_configure(config):
    results_dir = _get_allure_results_dir(config)
    results_dir.mkdir(exist_ok=True)

    environment = {
        "Application": "99acres",
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
        "name": "Local Windows Pytest",
        "type": "local",
        "buildName": "99acres New Launch Automation",
        "reportName": "99acres Automation Allure Report",
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


@pytest.fixture
def setup():
    options = webdriver.ChromeOptions()
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument(f"--window-size={ConfigReader.get('browser', 'window_size', '1920,1080')}")

    if ConfigReader.getboolean("browser", "headless", fallback=False):
        options.add_argument("--headless=new")

    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options,
    )
    driver.maximize_window()
    driver.set_page_load_timeout(ConfigReader.getint("browser", "page_load_timeout", 60))
    driver.execute_cdp_cmd(
        "Page.addScriptToEvaluateOnNewDocument",
        {"source": "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"},
    )
    driver.get(ConfigReader.get("application", "base_url"))

    yield driver   # test runs here

    try:
        driver.quit()
    except Exception:
        pass


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()

    if report.when != "call":
        return

    driver = item.funcargs.get("setup")
    if driver is None:
        return

    status = "passed" if report.passed else "failed" if report.failed else "skipped"
    try:
        allure.attach(
            driver.get_screenshot_as_png(),
            name=f"{item.name}_{status}",
            attachment_type=allure.attachment_type.PNG,
        )
    except Exception:
        pass
