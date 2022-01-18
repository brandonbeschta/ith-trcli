import random
from locust import HttpUser, task, between, events
from requests.auth import HTTPBasicAuth

HOST = "https://lchoj.testrail-staging.com/"
PREFIX = "index.php?"
VERSION = "/api/v2/"
API_V2_VERSION = f"{PREFIX}{VERSION}"


@events.init_command_line_parser.add_listener
def _(parser):
    parser.add_argument(
        "--user",
        type=str,
        env_var="LOCUST_TESTRAIL_USER",
        default="",
        help="User name for test rail stress testing.",
        include_in_web_ui=False,
        required=True,
    )
    parser.add_argument(
        "--password",
        type=str,
        env_var="LOCUST_TESTRAIL_PASS",
        include_in_web_ui=False,
        default="",
        help="Password/api_key for given user.",
        required=True,
    )


class TestRailBasicTasks(HttpUser):
    wait_time = between(1, 5)
    host = HOST

    @task
    def get_projects(self):
        self.client.get(
            f"{API_V2_VERSION}get_projects",
            auth=self._return_auth(),
            name="/get_projects",
        )

    @task
    def get_suites(self):
        projects_id = [1, 3, 4, 5, 6, 7]
        self.client.get(
            f"{API_V2_VERSION}get_suites/{random.choice(projects_id)}",
            auth=self._return_auth(),
            name="/get_suites",
        )

    @task
    def get_cases(self):
        project_suite_pairs = [(11, 727), (1, 460)]
        project_id, suite_id = random.choice(project_suite_pairs)

        self.client.get(
            f"{API_V2_VERSION}get_cases/{project_id}&suite_id={suite_id}",
            auth=self._return_auth(),
            name="/get_cases",
        )

    @task
    def get_results(self):
        test_id = [67064, 67065, 67066, 67067, 67068, 67069]
        self.client.get(
            f"{API_V2_VERSION}get_results/{random.choice(test_id)}",
            auth=self._return_auth(),
            name="/get_results",
        )

    def _return_auth(self):
        return HTTPBasicAuth(
            username=self.environment.parsed_options.user,
            password=self.environment.parsed_options.password,
        )
