from typing import Tuple

from trcli.api.api_client import APIClient
from trcli.cli import Environment
from trcli.api.api_request_handler import ApiRequestHandler
from trcli.constants import PROMPT_MESSAGES, FAULT_MAPPING
from trcli.data_classes.dataclass_testrail import TestRailSuite
from trcli.readers.file_parser import FileParser


class ResultsUploader:
    def __init__(self, environment: Environment, result_file_parser: FileParser):
        self.environment = environment
        self.result_file_parser = result_file_parser
        self.parsed_data: TestRailSuite = self.result_file_parser.parse_file()
        if self.environment.suite_id:
            self.parsed_data.suite_id = self.environment.suite_id
        self.api_request_handler = ApiRequestHandler(
            env=self.environment,
            api_client=self.__instantiate_api_client(),
            suites_data=self.parsed_data,
        )

    def upload_results(self):
        (
            project_id,
            project_suite_mode,
            error_message,
        ) = self.api_request_handler.get_project_data(self.environment.project)
        if project_id == -1:
            self.environment.log(FAULT_MAPPING["missing_project"])
            exit(1)
        elif project_id == -2:
            self.environment.log(
                FAULT_MAPPING["error_checking_project"].format(
                    error_message=error_message
                )
            )
            exit(1)
        else:
            pass
            suite_id = self.__get_suite_id_log_errors(project_id=project_id)
            if suite_id == -1:
                exit(1)

            added_sections, result_code = self.__check_for_missing_sections_and_add(
                project_id
            )
            if result_code == -1:
                exit(1)

            (
                added_test_cases,
                result_code,
            ) = self.__check_for_missing_test_cases_and_add()
            if result_code == -1:
                exit(1)

            self.environment.log(f"Creating test run.")
            added_run, error_message = self.api_request_handler.add_run(
                project_id, self.environment.title
            )
            if error_message:
                self.environment.log(error_message)
                exit(1)
            self.environment.log("Done.")

            added_results, error_message = self.api_request_handler.add_results(
                added_run
            )
            if error_message:
                self.environment.log(error_message)
                exit(1)

            self.environment.log("Closing test run.")
            response, error_message = self.api_request_handler.close_run(added_run)
            if error_message:
                self.environment.log(error_message)
                exit(1)
            self.environment.log("Done.")

    def __get_suite_id_log_errors(self, project_id: int) -> int:
        """side effect: sets suite_id under parsed data"""
        suite_id = -1
        # TODO: need to take parsed_data from api_request_handler directly. DO NOT USE LOCAL VARIABLE!!!!
        if not self.parsed_data.suite_id:
            if self.environment.get_prompt_response_for_auto_creation(
                PROMPT_MESSAGES["create_new_suite"].format(
                    suite_name=self.parsed_data.name,
                    project_name=self.environment.project,
                )
            ):
                # TODO: Why list is returned here?
                self.environment.log(
                    f"Adding missing suites to project {self.environment.project}."
                )
                added_suite = self.api_request_handler.add_suite(project_id)
                suite_id = added_suite[0]["suite_id"]
            else:
                self.environment.log(
                    FAULT_MAPPING["no_user_agreement"].format(type="suite")
                )
        else:
            suite_id = self.__check_suite_id_log_errors(
                self.parsed_data.suite_id, project_id
            )
        return suite_id

    def __check_suite_id_log_errors(self, suite_id, project_id) -> int:
        self.parsed_data.suite_id = suite_id
        if self.api_request_handler.check_suite_id(project_id):
            return suite_id
        else:
            self.environment.log(
                FAULT_MAPPING["missing_suite"].format(suite_id=suite_id)
            )
            return -1

    def __check_for_missing_sections_and_add(self, project_id: int) -> Tuple[list, int]:
        added_sections = []
        result_code = -1
        if self.api_request_handler.check_missing_section_id(project_id):
            if self.environment.get_prompt_response_for_auto_creation(
                PROMPT_MESSAGES["create_missing_sections"].format(
                    project_name=self.environment.project
                )
            ):
                added_sections, error_message = self.api_request_handler.add_section(
                    project_id=project_id
                )
                if error_message:
                    self.environment.log(error_message)
                else:
                    result_code = 1
            else:
                self.environment.log(
                    FAULT_MAPPING["no_user_agreement"].format(type="sections")
                )
        else:
            result_code = 1
        return added_sections, result_code

    def __check_for_missing_test_cases_and_add(self) -> Tuple[list, int]:
        added_cases = []
        result_code = -1
        if self.api_request_handler.check_missing_test_cases_ids():
            if self.environment.get_prompt_response_for_auto_creation(
                PROMPT_MESSAGES["create_missing_test_cases"].format(
                    project_name=self.environment.project
                )
            ):
                added_cases, error_message = self.api_request_handler.add_case()
                if error_message:
                    self.environment.log(error_message)
                else:
                    result_code = 1
            else:
                self.environment.log(
                    FAULT_MAPPING["no_user_agreement"].format(type="test cases")
                )
        else:
            result_code = 1
        return added_cases, result_code

    def __instantiate_api_client(self):
        if self.environment.timeout:
            api_client = APIClient(
                self.environment.host,
                timeout=self.environment.timeout
            )
        else:
            api_client = APIClient(
                self.environment.host
            )
        api_client.username = self.environment.username
        api_client.password = self.environment.password
        api_client.api_key = self.environment.key
        return api_client
