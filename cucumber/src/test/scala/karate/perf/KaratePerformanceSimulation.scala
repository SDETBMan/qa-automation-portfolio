package karate.perf

import com.intuit.karate.gatling.PreDef._
import io.gatling.core.Predef._

import scala.concurrent.duration._

class KaratePerformanceSimulation extends Simulation {

  val usersProtocol = karateProtocol(
    "/users/{id}" -> Nil
  )

  val postsProtocol = karateProtocol(
    "/posts/{id}" -> Nil
  )

  val commentsProtocol = karateProtocol(
    "/comments" -> Nil
  )

  val usersScenario = scenario("Users API")
    .exec(karateFeature("classpath:karate/api/users/users-crud.feature"))

  val postsScenario = scenario("Posts API")
    .exec(karateFeature("classpath:karate/api/posts/posts.feature"))

  val commentsScenario = scenario("Comments API")
    .exec(karateFeature("classpath:karate/api/comments/comments.feature"))

  setUp(
    usersScenario.inject(rampUsers(10).during(30.seconds)).protocols(usersProtocol),
    postsScenario.inject(rampUsers(10).during(30.seconds)).protocols(postsProtocol),
    commentsScenario.inject(rampUsers(5).during(30.seconds)).protocols(commentsProtocol)
  ).assertions(
    global.responseTime.mean.lt(500),
    global.responseTime.percentile(95).lt(2000),
    global.successfulRequests.percent.gt(95.0)
  )

}
