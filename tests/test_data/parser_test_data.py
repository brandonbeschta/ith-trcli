XML_NO_ROOT = """<?xml version="1.0" encoding="UTF-8"?>
<testsuite failures="1" errors="0" skipped="0" tests="2" time="0.05" name="One passing scenario, one failing scenario">
<testcase classname="One passing scenario, one failing scenario" name="Passing" time="0.05"></testcase>
<testcase classname="One passing scenario, one failing scenario" name="Failing" time="0.05">
  <failure message="failed Failing" type="failed"> FAILURE - No connection</failure></testcase>
</testsuite>"""
XML_ROOT = """<?xml version="1.0" encoding="UTF-8"?>
<testsuites name="test suites root" id="123">
<testsuite id="321" failures="0" errors="0" skipped="1" tests="1" time="0.05" name="Skipped test">
<properties><property name="setting1" value="True"/></properties>
<testcase id="666" classname="tests.test_junit_to_dataclass" name="test_testrail_test_suite" time="159">
<skipped type="pytest.skip" message="Please skip">skipped by user</skipped></testcase>
</testsuite></testsuites>"""
XML_EMPTY = """<?xml version="1.0" encoding="UTF-8"?>
<testsuites>
<testsuite>
<testcase></testcase>
<testcase ><failure></failure></testcase>
</testsuite></testsuites>"""
XML_INVALID = """<b>SOME TXT INVALID FILE</b>"""

EXPECTED_NO_ROOT = {
    "id": None,
    "name": None,
    "time": 0.1,
    "testsuites": [
        {
            "name": "One passing scenario, one failing scenario",
            "properties": [],
            "suite_id": None,
            "time": 0.05,
            "testcases": [
                {
                    "case_id": None,
                    "name": "Passing",
                    "time": 0.05,
                    "results": [],
                    "section_id": None,
                    "status_id": 1,
                },
                {
                    "case_id": None,
                    "name": "Failing",
                    "time": 0.05,
                    "section_id": None,
                    "status_id": 5,
                    "results": [
                        {
                            "message": "failed Failing",
                            "tag": "failure",
                            "text": " FAILURE - No connection",
                            "type": "failed",
                        }
                    ],
                },
            ],
        }
    ],
}

EXPECTED_ROOT = {
    "id": "123",
    "name": "test suites root",
    "time": 159,
    "testsuites": [
        {
            "name": "Skipped test",
            "properties": [
                {"description": "setting1: True", "name": "setting1", "value": "True"}
            ],
            "suite_id": "321",
            "time": 0.05,
            "testcases": [
                {
                    "case_id": "666",
                    "name": "test_testrail_test_suite",
                    "time": 159,
                    "section_id": "321",
                    "status_id": 4,
                    "results": [
                        {
                            "message": "Please skip",
                            "tag": "skipped",
                            "text": "skipped by user",
                            "type": "pytest.skip",
                        }
                    ],
                }
            ],
        }
    ],
}

EXPECTED_EMPTY = {
    "id": None,
    "name": None,
    "time": 0.0,
    "testsuites": [
        {
            "name": None,
            "properties": [],
            "suite_id": None,
            "time": 0.0,
            "testcases": [
                {
                    "case_id": None,
                    "name": None,
                    "time": None,
                    "section_id": None,
                    "status_id": 1,
                    "results": [],
                },
                {
                    "case_id": None,
                    "name": None,
                    "time": None,
                    "section_id": None,
                    "status_id": 5,
                    "results": [
                        {
                            "message": None,
                            "tag": "failure",
                            "text": None,
                            "type": None,
                        }
                    ],
                },
            ],
        }
    ],
}
