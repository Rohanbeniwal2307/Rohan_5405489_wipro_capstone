from datetime import datetime
from pathlib import Path

import allure


def take_screenshot(driver, name="screenshot"):
    screenshots_dir = Path("screenshots")
    screenshots_dir.mkdir(exist_ok=True)

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    safe_name = "".join(char if char.isalnum() or char in ("_", "-") else "_" for char in name)
    file_path = screenshots_dir / f"{safe_name}_{timestamp}.png"

    driver.save_screenshot(str(file_path))
    absolute_path = str(file_path.resolve())

    allure.attach.file(
        absolute_path,
        name=safe_name,
        attachment_type=allure.attachment_type.PNG,
    )
    return absolute_path
