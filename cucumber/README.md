# cucumber

[![cucumber CI](https://github.com/SDETBMan/qa-automation-portfolio/actions/workflows/cucumber.yml/badge.svg)](https://github.com/SDETBMan/qa-automation-portfolio/actions/workflows/cucumber.yml)
[![Java](https://img.shields.io/badge/Java-17-ED8B00?logo=openjdk)](https://openjdk.org/)
[![Cucumber](https://img.shields.io/badge/Cucumber-7.18-23D96C?logo=cucumber)](https://cucumber.io/)
[![Selenium](https://img.shields.io/badge/Selenium-4.21-43B02A?logo=selenium)](https://www.selenium.dev/)

BDD test automation framework using **Cucumber-JVM 7 + Selenium 4 + Java 17**,
targeting [SauceDemo](https://www.saucedemo.com/).

Demonstrates how Gherkin feature files serve as living documentation that
non-technical stakeholders can read and contribute to — complementing the
code-first approach in `selenium-java/` and `playwright-dotnet/`.

---

## Key Features

- **Gherkin feature files** — human-readable scenarios with Background, Scenario Outline, and Examples tables
- **Page Object Model** — clean separation of locators and actions from step definitions
- **Cucumber hooks** — `@Before`/`@After` for driver lifecycle and screenshot on failure
- **Tag-based execution** — `@smoke`, `@regression`, `@login`, `@inventory`, `@cart`
- **Allure reporting** — rich HTML reports via `allure-cucumber7-jvm` integration
- **Thread-safe driver** — `ThreadLocal<WebDriver>` for parallel scenario support
- **WebDriverManager** — automatic ChromeDriver/GeckoDriver management, no manual setup

---

## Tech Stack

| Component | Technology |
|---|---|
| Language | Java 17 |
| Build | Maven |
| BDD framework | Cucumber-JVM 7.18 |
| Test runner | JUnit 4 (`@RunWith(Cucumber.class)`) |
| Browser automation | Selenium 4.21 |
| Driver management | WebDriverManager 5.9 |
| Reporting | Allure + Cucumber HTML |
| CI/CD | GitHub Actions |

---

## Project Structure

```
cucumber/
├── pom.xml
├── src/
│   ├── main/java/com/cucumber/framework/
│   │   ├── driver/
│   │   │   └── DriverManager.java        # ThreadLocal WebDriver lifecycle
│   │   ├── pages/
│   │   │   ├── BasePage.java             # Explicit-wait helpers
│   │   │   ├── LoginPage.java
│   │   │   ├── InventoryPage.java
│   │   │   └── CartPage.java
│   │   └── utils/
│   │       └── ConfigReader.java         # Properties + system-property override
│   └── test/
│       ├── java/com/cucumber/framework/
│       │   ├── hooks/
│       │   │   └── Hooks.java            # @Before driver init, @After screenshot + quit
│       │   ├── runners/
│       │   │   └── TestRunner.java       # @CucumberOptions — features, glue, plugins
│       │   └── steps/
│       │       ├── LoginSteps.java       # login.feature + shared "I am logged in" step
│       │       ├── InventorySteps.java   # inventory.feature
│       │       └── CartSteps.java        # cart.feature
│       └── resources/
│           ├── config.properties
│           └── features/
│               ├── login.feature
│               ├── inventory.feature
│               └── cart.feature
└── README.md
```

---

## Quick Start

**Prerequisites:** [JDK 17](https://adoptium.net/) · [Maven 3.8+](https://maven.apache.org/)

```bash
cd cucumber

# Run all smoke + regression tests (headless)
mvn clean test -Dheadless=true

# Run smoke tests only
mvn clean test -Dcucumber.filter.tags="@smoke" -Dheadless=true

# Run a specific feature tag
mvn clean test -Dcucumber.filter.tags="@login" -Dheadless=true

# Run headed (for debugging)
mvn clean test -Dcucumber.filter.tags="@smoke"

# Generate and open Allure report
mvn allure:serve
```

---

## Feature File Example

```gherkin
@login
Feature: User Authentication

  Background:
    Given I am on the login page

  @smoke
  Scenario: Valid login navigates to inventory
    When I log in with username "standard_user" and password "secret_sauce"
    Then I should be on the inventory page

  @regression
  Scenario Outline: Multiple personas can log in successfully
    When I log in with username "<username>" and password "secret_sauce"
    Then I should be on the inventory page

    Examples:
      | username                |
      | standard_user           |
      | problem_user            |
      | performance_glitch_user |
```

---

## Test Tags

| Tag | Description | Filter |
|---|---|---|
| `@smoke` | Critical happy-path scenarios | `-Dcucumber.filter.tags="@smoke"` |
| `@regression` | Full negative + edge cases | `-Dcucumber.filter.tags="@regression"` |
| `@login` | All login scenarios | `-Dcucumber.filter.tags="@login"` |
| `@inventory` | Cart add/remove scenarios | `-Dcucumber.filter.tags="@inventory"` |
| `@cart` | Cart page + checkout scenarios | `-Dcucumber.filter.tags="@cart"` |

---

## Comparison: BDD vs Code-First

| Concern | cucumber (this) | selenium-java |
|---|---|---|
| Test definition | Gherkin `.feature` files | Java test methods |
| Stakeholder readable | Yes — plain English | No — requires Java knowledge |
| Step reuse | Shared step defs across features | Shared base classes / utilities |
| Reporting | Cucumber HTML + Allure | Allure TestNG |
| Runner | `@RunWith(Cucumber.class)` | TestNG XML suite |
| Driver lifecycle | Cucumber `@Before`/`@After` hooks | TestNG `@BeforeMethod`/`@AfterMethod` |
