# 99acres Selenium BDD Framework

This is the Behave BDD version of the 99acres New Launch automation project.

## Structure

```text
SeleniumBDD/99acres/
  config/              Application and test configuration
  features/            BDD feature files and Behave hooks
    steps/             Step definitions
  pages/               Selenium Page Object Model classes
  utilities/           Reusable helpers for logging, screenshots, and base actions
  test_data/           External test data
  logs/                Runtime logs
  screenshots/         Runtime screenshots
  allure-results/      Allure raw results
  reports/             Optional generated reports
```

## Run Positive And Negative Scenarios

```powershell
cd C:\99acres-framework\SeleniumBDD\99acres
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
& C:\99acres-framework\venv\Scripts\Activate.ps1
behave features/newlaunch_positive_negative.feature -f allure_behave.formatter:AllureFormatter -o allure-results
```

## Run End To End Scenario

```powershell
cd C:\99acres-framework\SeleniumBDD\99acres
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
& C:\99acres-framework\venv\Scripts\Activate.ps1
behave features/newlaunch_end_to_end.feature -f allure_behave.formatter:AllureFormatter -o allure-results
```

## Generate And Open Allure Report

```powershell
$env:JAVA_HOME='C:\Users\ROHAN\scoop\apps\temurin17-jdk\current'
$env:Path="$env:JAVA_HOME\bin;$env:Path"
allure generate allure-results --clean -o allure-report
cd allure-report
python -m http.server 8000 --bind 127.0.0.1
```
