from junitparser import TestCase, TestSuite, JUnitXml, Skipped, Error

error = """
project = Project( name=self.project_config.project_info.project_name, show_announcement=False, announcement="Some announcement", suite_mode=1,
)
self.project = self.api_client.add_project(project)

self.project_page.open_page(self.data.server_name)
self.login_page.simple_login(self.data.login.username, self.data.login.password)

self.project_page.open_page(
    self.data.server_name
    + self.project_config.project_overview_url
    + str(self.project.id)
)
self.suite_id = self.section_page.open_test_cases()
section = Section(name="Section", description="desc", suite_id=self.suite_id)
self.section = self.api_client.add_section(section, self.project.id)
self.case = self.api_client.add_case(Case(title="Test Case"), self.section.id)
run = Run( name="Test Run", description="This is a test run", suite_id=self.suite_id, include_all=True,
)
self.run = self.api_client.add_run(run, self.project.id)
self.plan = self.api_client.add_plan(Plan(name="Plan"), self.project.id)
self.testcase_edit_url = (
    self.data.server_name
    + self.tests_config.edit_test_case_url
    + str(self.case.id)
)
self.run_edit_url = (
    self.data.server_name + self.runs_config.edit_url + str(self.run.id)
)
self.run_overview_url = (
    self.data.server_name + self.runs_config.overview_url + str(self.project.id)
)
self.edit_plan_url = (
    self.data.server_name + self.plans_config.edit_url + str(self.plan.id)
)
self.suite_overview_url = (
    self.data.server_name
    + self.project_config.suites.view_url
    + str(self.suite_id)
)
self.all_projects_option = (
    self.attachments_config.attachment_details_all_projects_option
)
self.attachments_page.open_list_and_delete_all_attachmnets(
       self.data_management_url, HOSTED
)

test_attachments.py:112:
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _
/administration/attachments_page.py:438: in open_list_and_delete_all_attachmnets
.open_attachments_tab()
/administration/attachments_page.py:41: in open_attachments_tab
.wait_for_blockui_to_close()
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _

lt;src.pages.administration.attachments_page.AttachmentsPage object at 0x7f39c79d37b8&gt;
= 7

wait_for_blockui_to_close(self, seconds=7):
self.driver.implicitly_wait(0)
try:
    stop = time.time() + seconds
    while time.time() &lt; stop:
        blockUIs = self.find_elements_by_locator(GeneralLocators.blockUI)
        if not any_elements_displayed(blockUIs):
            return
        time.sleep(0.1)
       raise TimeoutException("Timed out waiting for blockUI to go away")
    selenium.common.exceptions.TimeoutException: Message: Timed out waiting for blockUI to go away

/base_element.py:75: TimeoutException"""

# Create suite and add cases
suite = TestSuite("Performance_Tests")
for i in range(5000):
    case1 = TestCase(f"case{i}")  # params are optional
    case1.result = [Error(error, "the_error_type")]
    suite.add_testcase(case1)


# Add suite to JunitXml
xml = JUnitXml()
xml.add_testsuite(suite)
xml.write("junit_big_error_5000.xml")
