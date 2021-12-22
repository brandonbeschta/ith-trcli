import pytest
from trcli.api.results_uploader import ResultsUploader
from trcli.cli import Environment
from trcli.constants import FAULT_MAPPING, PROMPT_MESSAGES
from trcli.readers.junit_xml import JunitParser
from trcli.api.api_request_handler import ProjectData
from trcli.constants import ProjectErrors


class TestResultsUploader:
    @pytest.fixture(scope="function")
    def result_uploader_data_provider(self, mocker):
        environment = mocker.patch("trcli.api.results_uploader.Environment")
        environment.host = "https://lchoj.testrail-staging.com/"
        environment.project = "Fake project name"

        junit_file_parser = mocker.patch.object(JunitParser, "parse_file")
        api_request_handler = mocker.patch(
            "trcli.api.results_uploader.ApiRequestHandler"
        )

        yield environment, junit_file_parser, api_request_handler

    @pytest.mark.results_uploader
    def test_project_name_missing_in_test_rail(
        self, result_uploader_data_provider, mocker
    ):
        """The purpose of this test is to check that proper message will be printed when project with name provided
        does not exist in TestRail."""
        (
            environment,
            junit_file_parser,
            api_request_handler,
        ) = result_uploader_data_provider
        result_uploader = ResultsUploader(
            environment=environment, result_file_parser=junit_file_parser
        )
        result_uploader.api_request_handler.get_project_id.return_value = ProjectData(project_id=ProjectErrors.not_existing_project,
                                                                                      suite_mode=-1,
                                                                                      error_message=f"{environment.project} project doesn't exists.")

        with pytest.raises(SystemExit) as exception:
            _ = result_uploader.upload_results()

        environment.log.assert_called_with(f"{environment.project} project doesn't exists.")
        assert (
            exception.type == SystemExit
        ), f"Expected SystemExit exception, but got {exception.type} instead."
        assert (
            exception.value.code == 1
        ), f"Expected exit code 1, but got {exception.value.code} instead."

    @pytest.mark.results_uploader
    def test_error_during_checking_of_project(self, result_uploader_data_provider):
        (
            environment,
            junit_file_parser,
            api_request_handler,
        ) = result_uploader_data_provider
        result_uploader = ResultsUploader(
            environment=environment, result_file_parser=junit_file_parser
        )
        result_uploader.api_request_handler.get_project_id.return_value = ProjectData(project_id=ProjectErrors.other_error,
                                                                                      suite_mode=-1,
                                                                                      error_message="Unable to connect")

        with pytest.raises(SystemExit) as exception:
            _ = result_uploader.upload_results()

        environment.log.assert_called_with(FAULT_MAPPING["error_checking_project"].format(error_message="Unable to connect"))
        assert (
                exception.type == SystemExit
        ), f"Expected SystemExit exception, but got {exception.type} instead."
        assert (
                exception.value.code == 1
        ), f"Expected exit code 1, but got {exception.value.code} instead."

    @pytest.mark.results_uploader
    def test_failed_to_get_suite_id(self, result_uploader_data_provider, mocker):
        (
            environment,
            junit_file_parser,
            api_request_handler,
        ) = result_uploader_data_provider
        project_id = 10
        result_uploader = ResultsUploader(
            environment=environment, result_file_parser=junit_file_parser
        )
        result_uploader.api_request_handler.get_project_id.return_value = ProjectData(project_id=10,
                                                                                      suite_mode=1,
                                                                                      error_message="")
        result_uploader._ResultsUploader__get_suite_id_log_errors = mocker.Mock()
        result_uploader._ResultsUploader__get_suite_id_log_errors.return_value = -1

        with pytest.raises(SystemExit) as exception:
            _ = result_uploader.upload_results()

        assert (
                exception.type == SystemExit
        ), f"Expected SystemExit exception, but got {exception.type} instead."
        assert (
                exception.value.code == 1
        ), f"Expected exit code 1, but got {exception.value.code} instead."

    @pytest.mark.results_uploader
    def test_check_and_add_sections_failed(self, result_uploader_data_provider, mocker):
        (
            environment,
            junit_file_parser,
            api_request_handler,
        ) = result_uploader_data_provider
        project_id = 10
        result_uploader = ResultsUploader(
            environment=environment, result_file_parser=junit_file_parser
        )
        result_uploader.api_request_handler.get_project_data.return_value = (project_id, 1, "")
        result_uploader._ResultsUploader__get_suite_id_log_errors = mocker.Mock()
        result_uploader._ResultsUploader__get_suite_id_log_errors.return_value = 5
        result_uploader._ResultsUploader__check_for_missing_sections_and_add = mocker.Mock()
        result_uploader._ResultsUploader__check_for_missing_sections_and_add.return_value = ([], -1)

        with pytest.raises(SystemExit) as exception:
            _ = result_uploader.upload_results()

        assert (
                exception.type == SystemExit
        ), f"Expected SystemExit exception, but got {exception.type} instead."
        assert (
                exception.value.code == 1
        ), f"Expected exit code 1, but got {exception.value.code} instead."

    @pytest.mark.results_uploader
    def test_check_and_add_test_cases_failed(self, result_uploader_data_provider, mocker):
        (
            environment,
            junit_file_parser,
            api_request_handler,
        ) = result_uploader_data_provider
        project_id = 10
        result_uploader = ResultsUploader(
            environment=environment, result_file_parser=junit_file_parser
        )
        result_uploader.api_request_handler.get_project_data.return_value = (project_id, 1, "")
        result_uploader._ResultsUploader__get_suite_id_log_errors = mocker.Mock()
        result_uploader._ResultsUploader__get_suite_id_log_errors.return_value = 5
        result_uploader._ResultsUploader__check_for_missing_sections_and_add = mocker.Mock()
        result_uploader._ResultsUploader__check_for_missing_sections_and_add.return_value = ([10], 1)
        result_uploader._ResultsUploader__check_for_missing_test_cases_and_add = mocker.Mock()
        result_uploader._ResultsUploader__check_for_missing_test_cases_and_add.return_value = ([], -1)

        with pytest.raises(SystemExit) as exception:
            _ = result_uploader.upload_results()

        assert (
                exception.type == SystemExit
        ), f"Expected SystemExit exception, but got {exception.type} instead."
        assert (
                exception.value.code == 1
        ), f"Expected exit code 1, but got {exception.value.code} instead."

    @pytest.mark.results_uploader
    @pytest.mark.test123
    def test_add_run_failed(self, result_uploader_data_provider, mocker):
        (
            environment,
            junit_file_parser,
            api_request_handler,
        ) = result_uploader_data_provider
        project_id = 10
        result_uploader = ResultsUploader(
            environment=environment, result_file_parser=junit_file_parser
        )
        result_uploader.api_request_handler.get_project_data.return_value = (project_id, 1, "")
        result_uploader._ResultsUploader__get_suite_id_log_errors = mocker.Mock()
        result_uploader._ResultsUploader__get_suite_id_log_errors.return_value = 5
        result_uploader._ResultsUploader__check_for_missing_sections_and_add = mocker.Mock()
        result_uploader._ResultsUploader__check_for_missing_sections_and_add.return_value = ([10], 1)
        result_uploader._ResultsUploader__check_for_missing_test_cases_and_add = mocker.Mock()
        result_uploader._ResultsUploader__check_for_missing_test_cases_and_add.return_value = ([10, 11], 1)
        result_uploader.api_request_handler.add_run.return_value = ([], "Failed to add run.")

        with pytest.raises(SystemExit) as exception:
            _ = result_uploader.upload_results()

        assert (
                exception.type == SystemExit
        ), f"Expected SystemExit exception, but got {exception.type} instead."
        assert (
                exception.value.code == 1
        ), f"Expected exit code 1, but got {exception.value.code} instead."

    @pytest.mark.results_uploader
    def test_add_results_failed(self, result_uploader_data_provider, mocker):
        (
            environment,
            junit_file_parser,
            api_request_handler,
        ) = result_uploader_data_provider
        project_id = 10
        result_uploader = ResultsUploader(
            environment=environment, result_file_parser=junit_file_parser
        )
        result_uploader.api_request_handler.get_project_data.return_value = (project_id, 1, "")
        result_uploader._ResultsUploader__get_suite_id_log_errors = mocker.Mock()
        result_uploader._ResultsUploader__get_suite_id_log_errors.return_value = 5
        result_uploader._ResultsUploader__check_for_missing_sections_and_add = mocker.Mock()
        result_uploader._ResultsUploader__check_for_missing_sections_and_add.return_value = ([10], 1)
        result_uploader._ResultsUploader__check_for_missing_test_cases_and_add = mocker.Mock()
        result_uploader._ResultsUploader__check_for_missing_test_cases_and_add.return_value = ([20, 30], 1)
        result_uploader.api_request_handler.add_run.return_value = ([100], "")
        result_uploader.api_request_handler.add_results.return_value = ([], "Failed to add results.")

        with pytest.raises(SystemExit) as exception:
            _ = result_uploader.upload_results()

        assert (
                exception.type == SystemExit
        ), f"Expected SystemExit exception, but got {exception.type} instead."
        assert (
                exception.value.code == 1
        ), f"Expected exit code 1, but got {exception.value.code} instead."

    @pytest.mark.results_uploader
    def test_close_run_failed(self, result_uploader_data_provider, mocker):
        (
            environment,
            junit_file_parser,
            api_request_handler,
        ) = result_uploader_data_provider
        project_id = 10
        result_uploader = ResultsUploader(
            environment=environment, result_file_parser=junit_file_parser
        )
        result_uploader.api_request_handler.get_project_data.return_value = (project_id, 1, "")
        result_uploader._ResultsUploader__get_suite_id_log_errors = mocker.Mock()
        result_uploader._ResultsUploader__get_suite_id_log_errors.return_value = 5
        result_uploader._ResultsUploader__check_for_missing_sections_and_add = mocker.Mock()
        result_uploader._ResultsUploader__check_for_missing_sections_and_add.return_value = ([10], 1)
        result_uploader._ResultsUploader__check_for_missing_test_cases_and_add = mocker.Mock()
        result_uploader._ResultsUploader__check_for_missing_test_cases_and_add.return_value = ([20, 30], 1)
        result_uploader.api_request_handler.add_run.return_value = ([100], "")
        result_uploader.api_request_handler.add_results.return_value = ([1, 2, 3], "")
        result_uploader.api_request_handler.close_run.return_value = ([], "Failed to close run.")

        with pytest.raises(SystemExit) as exception:
            _ = result_uploader.upload_results()

        assert (
                exception.type == SystemExit
        ), f"Expected SystemExit exception, but got {exception.type} instead."
        assert (
                exception.value.code == 1
        ), f"Expected exit code 1, but got {exception.value.code} instead."

    @pytest.mark.results_uploader
    def test_upload_results_successful(self, result_uploader_data_provider, mocker):
        (
            environment,
            junit_file_parser,
            api_request_handler,
        ) = result_uploader_data_provider
        project_id = 10
        result_uploader = ResultsUploader(
            environment=environment, result_file_parser=junit_file_parser
        )
        result_uploader.api_request_handler.get_project_data.return_value = (project_id, 1, "")
        result_uploader._ResultsUploader__get_suite_id_log_errors = mocker.Mock()
        result_uploader._ResultsUploader__get_suite_id_log_errors.return_value = 5
        result_uploader._ResultsUploader__check_for_missing_sections_and_add = mocker.Mock()
        result_uploader._ResultsUploader__check_for_missing_sections_and_add.return_value = ([10], 1)
        result_uploader._ResultsUploader__check_for_missing_test_cases_and_add = mocker.Mock()
        result_uploader._ResultsUploader__check_for_missing_test_cases_and_add.return_value = ([20, 30], 1)
        result_uploader.api_request_handler.add_run.return_value = ([100], "")
        result_uploader.api_request_handler.add_results.return_value = ([1, 2, 3], "")
        result_uploader.api_request_handler.close_run.return_value = ([100], "")

        _ = result_uploader.upload_results()
        environment.log.assert_any_call("Creating test run.")
        environment.log.assert_any_call("Done.")
        environment.log.assert_any_call("Closing test run.")
        environment.log.assert_any_call("Done.")

    @pytest.mark.results_uploader
    def test_get_suite_id_log_errors_returns_valid_id(
        self, result_uploader_data_provider
    ):
        """The purpose of this test is to check that __get_suite_id_log_errors function will
        return suite_id if it exists in TestRail"""
        (
            environment,
            junit_file_parser,
            api_request_handler,
        ) = result_uploader_data_provider
        suite_id = 10
        project_id = 1
        result_uploader = ResultsUploader(
            environment=environment, result_file_parser=junit_file_parser
        )
        result_uploader.api_request_handler.suites_data_from_provider.suite_id = suite_id
        result_uploader.api_request_handler.check_suite_id.return_value = True
        result = result_uploader._ResultsUploader__get_suite_id_log_errors(
            project_id=project_id
        )

        assert (
            result == suite_id
        ), f"Expected suite_id: {suite_id} but got {result} instead."

    @pytest.mark.results_uploader
    @pytest.mark.parametrize(
        "user_response, expected_suite_id, expected_message, suite_add_error",
        [
            (True, 10, "Adding missing suites to project Fake project name.", False),
            (True, -1, "Adding missing suites to project Fake project name.", True),
            (False, -1, FAULT_MAPPING["no_user_agreement"].format(type="suite"), False)
        ],
        ids=["user agrees", "user agrees, fail to add suite", "used does not agree"],
    )
    def test_get_suite_id_log_errors_prompts_user(
        self,
        user_response,
        expected_suite_id,
        expected_message,
        suite_add_error,
        result_uploader_data_provider,
    ):
        """The purpose of this test is to check that user will be prompted to add suite is one is missing in TestRail.
        Depending on user response either information about addition of missing suite or error message should be printed."""
        (
            environment,
            junit_file_parser,
            api_request_handler,
        ) = result_uploader_data_provider
        project_id = 1
        suite_name = "Fake suite name"

        result_uploader = ResultsUploader(
            environment=environment, result_file_parser=junit_file_parser
        )
        if not suite_add_error:
            result_uploader.api_request_handler.add_suite.return_value = ([
                {
                    "suite_id": expected_suite_id,
                    "name": suite_name,
                }
            ], "")
        else:
            result_uploader.api_request_handler.add_suite.return_value = ([
                {
                    "suite_id": -1,
                    "name": suite_name
                }
            ], "Failed to add suite.")
        result_uploader.api_request_handler.suites_data_from_provider.suite_id = None
        result_uploader.api_request_handler.suites_data_from_provider.name = suite_name
        environment.get_prompt_response_for_auto_creation.return_value = user_response
        result = result_uploader._ResultsUploader__get_suite_id_log_errors(project_id)

        assert (
            expected_suite_id == result
        ), f"Expected suite_id: {expected_suite_id} but got {result} instead."
        environment.get_prompt_response_for_auto_creation.assert_called_with(
            PROMPT_MESSAGES["create_new_suite"].format(
                suite_name=suite_name,
                project_name=environment.project,
            )
        )
        if user_response:
            result_uploader.api_request_handler.add_suite.assert_called_with(project_id)
        environment.log.assert_any_call(expected_message)
        if suite_add_error:
            environment.log.assert_any_call(FAULT_MAPPING["error_while_adding_suite"].format(error_message="Failed to add suite."))

    @pytest.mark.results_uploader
    def test_check_suite_id_log_errors_returns_id(self, result_uploader_data_provider):
        """The purpose of this test is to check that __check_suite_id_log_errors function will return suite ID,
        when suite ID exists under specified project."""
        (
            environment,
            junit_file_parser,
            api_request_handler,
        ) = result_uploader_data_provider

        result_uploader = ResultsUploader(
            environment=environment, result_file_parser=junit_file_parser
        )
        result_uploader.api_request_handler.check_suite_id.return_value = True

        result = result_uploader._ResultsUploader__check_suite_id_log_errors(
            suite_id=1, project_id=2
        )

        assert result == 1, f"Expected to get 1 as suite ID, but got {result} instead."

    @pytest.mark.results_uploader
    def test_check_suite_id_prints_error_message(self, result_uploader_data_provider):
        """The purpose of this test is to check that proper message would be printed to the user
        and program will quit when suite ID is not present in TestRail."""
        (
            environment,
            junit_file_parser,
            api_request_handler,
        ) = result_uploader_data_provider
        suite_id = 1
        result_uploader = ResultsUploader(
            environment=environment, result_file_parser=junit_file_parser
        )
        result_uploader.api_request_handler.check_suite_id.return_value = False

        result = result_uploader._ResultsUploader__check_suite_id_log_errors(
            suite_id=suite_id, project_id=2
        )

        environment.log.assert_called_with(
            FAULT_MAPPING["missing_suite"].format(suite_id=suite_id)
        )
        assert (
            result == -1
        ), f"Expected to get -1 as suite ID, but got {result} instead."

    @pytest.mark.results_uploader
    def test_check_for_missing_sections_no_missing_sections(
        self, result_uploader_data_provider
    ):
        (
            environment,
            junit_file_parser,
            api_request_handler,
        ) = result_uploader_data_provider
        project_id = 1
        missing_sections = []
        result_uploader = ResultsUploader(
            environment=environment, result_file_parser=junit_file_parser
        )
        result_uploader.api_request_handler.check_missing_section_id.return_value = (
            missing_sections,
            ""
        )
        result = result_uploader._ResultsUploader__check_for_missing_sections_and_add(
            project_id
        )

        assert result == (
            missing_sections,
            1,
        ), f"Expected to get {missing_sections, 1} as a result but got {result} instead."

    @pytest.mark.results_uploader
    @pytest.mark.parametrize(
        "user_response, missing_sections, expected_add_sections_error, expected_added_sections, expected_message, expected_result_code",
        [
            (
                True,
                [10, 11, 12],
                "",
                [10, 11, 12],
                "Adding missing sections to the suite.",
                1,
            ),
            (
                True,
                [10, 11, 12],
                "Fail to add",
                [],
                "Adding missing sections to the suite.",
                -1,
            ),
            (
                False,
                [10, 11, 12],
                "",
                [],
                FAULT_MAPPING["no_user_agreement"].format(type="sections"),
                -1,
            ),
        ],
        ids=[
            "user agrees, sections added",
            "user agrees, sections not added",
            "used does not agree",
        ],
    )
    def test_check_for_missing_sections_prompts_user(
        self,
        user_response,
        missing_sections,
        expected_add_sections_error,
        expected_added_sections,
        expected_message,
        expected_result_code,
        result_uploader_data_provider,
    ):
        (
            environment,
            junit_file_parser,
            api_request_handler,
        ) = result_uploader_data_provider
        project_id = 1
        result_uploader = ResultsUploader(
            environment=environment, result_file_parser=junit_file_parser
        )
        result_uploader.api_request_handler.check_missing_section_id.return_value = (
            missing_sections,
            ""
        )
        result_uploader.environment.get_prompt_response_for_auto_creation.return_value = (
            user_response
        )
        result_uploader.api_request_handler.add_section.return_value = (
            expected_added_sections,
            expected_add_sections_error
        )

        (
            result_added_sections,
            result_code,
        ) = result_uploader._ResultsUploader__check_for_missing_sections_and_add(
            project_id
        )

        assert (
            result_code == expected_result_code
        ), f"Expected result_code {expected_result_code} but got {result_code} instead."
        assert (
            result_added_sections == expected_added_sections
        ), f"Expected sections to be added: {expected_added_sections} but got {result_added_sections} instead."
        environment.log.assert_any_call(expected_message)
        if expected_add_sections_error:
            environment.log.assert_any_call(expected_add_sections_error)
        environment.get_prompt_response_for_auto_creation.assert_called_with(
            PROMPT_MESSAGES["create_missing_sections"].format(
                project_name=environment.project
            )
        )

    @pytest.mark.results_uploader
    def test_check_for_missing_test_cases_no_missing_test_cases(
        self, result_uploader_data_provider
    ):
        (
            environment,
            junit_file_parser,
            api_request_handler,
        ) = result_uploader_data_provider
        project_id = 1
        missing_test_cases = []
        result_uploader = ResultsUploader(
            environment=environment, result_file_parser=junit_file_parser
        )
        result_uploader.api_request_handler.check_missing_test_cases_ids.return_value = (
            missing_test_cases,
            ""
        )
        result = (
            result_uploader._ResultsUploader__check_for_missing_test_cases_and_add(project_id)
        )

        assert result == (
            missing_test_cases,
            1,
        ), f"Expected to get {(missing_test_cases, 1)} as a result but got {result} instead."

    @pytest.mark.results_uploader
    @pytest.mark.parametrize(
        "user_response, missing_test_cases, expected_add_test_cases_error, expected_added_test_cases, expected_message, expected_result_code",
        [
            (
                True,
                [10, 11, 12],
                "",
                [10, 11, 12],
                "Adding missing test cases to the suite.",
                1,
            ),
            (
                True,
                [10, 11, 12],
                "Fail to add",
                [],
                "Adding missing test cases to the suite.",
                -1,
            ),
            (
                False,
                [10, 11, 12],
                "",
                [],
                FAULT_MAPPING["no_user_agreement"].format(type="test cases"),
                -1,
            ),
        ],
        ids=[
            "user agrees, test cases added",
            "user agrees, test cases not added",
            "used does not agree",
        ],
    )
    def test_check_for_missing_test_cases_prompts_user(
        self,
        user_response,
        missing_test_cases,
        expected_add_test_cases_error,
        expected_added_test_cases,
        expected_message,
        expected_result_code,
        result_uploader_data_provider,
    ):
        (
            environment,
            junit_file_parser,
            api_request_handler,
        ) = result_uploader_data_provider
        project_id = 1
        result_uploader = ResultsUploader(
            environment=environment, result_file_parser=junit_file_parser
        )
        result_uploader.api_request_handler.check_missing_test_cases_ids.return_value = (
            missing_test_cases,
            expected_message
        )
        result_uploader.environment.get_prompt_response_for_auto_creation.return_value = (
            user_response
        )
        result_uploader.api_request_handler.add_case.return_value = (
            expected_added_test_cases,
            expected_add_test_cases_error,
        )

        (
            result_added_test_cases,
            result_code,
        ) = result_uploader._ResultsUploader__check_for_missing_test_cases_and_add(project_id)

        assert (
            result_code == expected_result_code
        ), f"Expected result_code {expected_result_code} but got {result_code} instead."
        assert (
            result_added_test_cases == expected_added_test_cases
        ), f"Expected test cases to be added: {expected_added_test_cases} but got {result_added_test_cases} instead."
        environment.log.assert_any_call(expected_message)
        if expected_add_test_cases_error:
            environment.log.assert_any_call(expected_add_test_cases_error)
        environment.get_prompt_response_for_auto_creation.assert_called_with(
            PROMPT_MESSAGES["create_missing_test_cases"].format(
                project_name=environment.project
            )
        )

    @pytest.mark.results_uploader
    @pytest.mark.parametrize(
        "timeout", [40, None], ids=["with_timeout", "without_timeout"]
    )
    def test_instantiate_api_client(self, timeout, result_uploader_data_provider):
        """The purpose of this test is to check that APIClient was instantiated properly and credential fields
        were set es expected."""
        (
            _,
            junit_file_parser,
            api_request_handler,
        ) = result_uploader_data_provider
        environment = Environment()
        environment.host = "https://fake_host.com"
        environment.username = "usermane@host.com"
        environment.password = "test_password"
        environment.key = "test_api_key"
        if timeout:
            environment.timeout = timeout
        timeout_expected_result = 30 if not timeout else timeout
        result_uploader = ResultsUploader(
            environment=environment, result_file_parser=junit_file_parser
        )

        api_client = result_uploader._ResultsUploader__instantiate_api_client()

        assert (
            api_client.username == environment.username
        ), f"Expected username to be set to: {environment.username}, but got: {api_client.username} instead."
        assert (
            api_client.password == environment.password
        ), f"Expected password  to be set to: {environment.password}, but got: {api_client.password} instead."
        assert (
            api_client.api_key == environment.key
        ), f"Expected api_key to be set to: {environment.key}, but got: {api_client.api_key} instead."
        assert (
            api_client.timeout == timeout_expected_result
        ), f"Expected timeout to be set to: {timeout_expected_result}, but got: {api_client.timeout} instead."
