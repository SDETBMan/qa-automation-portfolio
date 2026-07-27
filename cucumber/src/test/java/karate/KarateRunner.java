package karate;

import com.intuit.karate.junit5.Karate;

/**
 * JUnit5 runner for all Karate API tests.
 *
 * <p>Discovered by maven-surefire-plugin when the {@code karate} Maven profile is active.
 * The default profile excludes this class so {@code mvn test} runs only Cucumber.
 *
 * <p>Run commands:
 * <ul>
 *   <li>{@code mvn clean test -Pkarate} — all Karate features</li>
 *   <li>{@code mvn clean test -Pkarate -Dkarate.env=staging} — target staging env</li>
 *   <li>{@code mvn clean test -Pkarate -Dkarate.options="--tags @smoke"} — tagged subset</li>
 * </ul>
 */
class KarateRunner {

    @Karate.Test
    Karate testAll() {
        return Karate.run("classpath:karate")
                .relativeTo(this.getClass());
    }
}
