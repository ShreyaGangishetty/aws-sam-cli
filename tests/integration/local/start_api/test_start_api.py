import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
from time import time

import pytest

from samcli.local.apigw.local_apigw_service import Route
from .start_api_integ_base import StartApiIntegBaseClass


class TestParallelRequests(StartApiIntegBaseClass):
    """
    Test Class centered around sending parallel requests to the service `sam local start-api`
    """

    # This is here so the setUpClass doesn't fail. Set to this something else once the class is implemented
    template_path = "/testdata/start_api/template.yaml"

    def setUp(self):
        self.url = "http://127.0.0.1:{}".format(self.port)

    @pytest.mark.timeout(timeout=600, method="thread")
    def test_same_endpoint(self):
        """
        Send two requests to the same path at the same time. This is to ensure we can handle
        multiple requests at once and do not block/queue up requests
        """
        number_of_requests = 10
        start_time = time()
        thread_pool = ThreadPoolExecutor(number_of_requests)

        futures = [
            thread_pool.submit(requests.get, self.url + "/sleepfortenseconds/function1")
            for _ in range(0, number_of_requests)
        ]
        results = [r.result() for r in as_completed(futures)]

        end_time = time()

        self.assertEqual(len(results), 10)
        self.assertGreater(end_time - start_time, 10)

        for result in results:
            self.assertEqual(result.status_code, 200)
            self.assertEqual(result.json(), {"message": "HelloWorld! I just slept and waking up."})

    @pytest.mark.timeout(timeout=600, method="thread")
    def test_different_endpoints(self):
        """
        Send two requests to different paths at the same time. This is to ensure we can handle
        multiple requests for different paths and do not block/queue up the requests
        """
        number_of_requests = 10
        start_time = time()
        thread_pool = ThreadPoolExecutor(10)

        test_url_paths = ["/sleepfortenseconds/function0", "/sleepfortenseconds/function1"]

        futures = [
            thread_pool.submit(requests.get, self.url + test_url_paths[function_num % len(test_url_paths)])
            for function_num in range(0, number_of_requests)
        ]
        results = [r.result() for r in as_completed(futures)]

        end_time = time()

        self.assertEqual(len(results), 10)
        self.assertGreater(end_time - start_time, 10)

        for result in results:
            self.assertEqual(result.status_code, 200)
            self.assertEqual(result.json(), {"message": "HelloWorld! I just slept and waking up."})


class TestServiceErrorResponses(StartApiIntegBaseClass):
    """
    Test Class centered around the Error Responses the Service can return for a given api
    """

    # This is here so the setUpClass doesn't fail. Set to this something else once the class is implemented.
    template_path = "/testdata/start_api/template.yaml"

    def setUp(self):
        self.url = "http://127.0.0.1:{}".format(self.port)

    @pytest.mark.timeout(timeout=600, method="thread")
    def test_invalid_http_verb_for_endpoint(self):
        response = requests.get(self.url + "/id")

        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.json(), {"message": "Missing Authentication Token"})

    @pytest.mark.timeout(timeout=600, method="thread")
    def test_invalid_response_from_lambda(self):
        response = requests.get(self.url + "/invalidresponsereturned")

        self.assertEqual(response.status_code, 502)
        self.assertEqual(response.json(), {"message": "Internal server error"})

    @pytest.mark.timeout(timeout=600, method="thread")
    def test_invalid_json_response_from_lambda(self):
        response = requests.get(self.url + "/invalidresponsehash")

        self.assertEqual(response.status_code, 502)
        self.assertEqual(response.json(), {"message": "Internal server error"})

    @pytest.mark.timeout(timeout=600, method="thread")
    def test_request_timeout(self):
        pass


class TestService(StartApiIntegBaseClass):
    """
    Testing general requirements around the Service that powers `sam local start-api`
    """

    template_path = "/testdata/start_api/template.yaml"

    def setUp(self):
        self.url = "http://127.0.0.1:{}".format(self.port)

    def test_static_directory(self):
        pass

    @pytest.mark.timeout(timeout=600, method="thread")
    def test_calling_proxy_endpoint(self):
        response = requests.get(self.url + "/proxypath/this/is/some/path")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"hello": "world"})

    @pytest.mark.timeout(timeout=600, method="thread")
    def test_get_call_with_path_setup_with_any_implicit_api(self):
        """
        Get Request to a path that was defined as ANY in SAM through AWS::Serverless::Function Events
        """
        response = requests.get(self.url + "/anyandall")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"hello": "world"})

    @pytest.mark.timeout(timeout=600, method="thread")
    def test_post_call_with_path_setup_with_any_implicit_api(self):
        """
        Post Request to a path that was defined as ANY in SAM through AWS::Serverless::Function Events
        """
        response = requests.post(self.url + "/anyandall", json={})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"hello": "world"})

    @pytest.mark.timeout(timeout=600, method="thread")
    def test_put_call_with_path_setup_with_any_implicit_api(self):
        """
        Put Request to a path that was defined as ANY in SAM through AWS::Serverless::Function Events
        """
        response = requests.put(self.url + "/anyandall", json={})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"hello": "world"})

    @pytest.mark.timeout(timeout=600, method="thread")
    def test_head_call_with_path_setup_with_any_implicit_api(self):
        """
        Head Request to a path that was defined as ANY in SAM through AWS::Serverless::Function Events
        """
        response = requests.head(self.url + "/anyandall")

        self.assertEqual(response.status_code, 200)

    @pytest.mark.timeout(timeout=600, method="thread")
    def test_delete_call_with_path_setup_with_any_implicit_api(self):
        """
        Delete Request to a path that was defined as ANY in SAM through AWS::Serverless::Function Events
        """
        response = requests.delete(self.url + "/anyandall")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"hello": "world"})

    @pytest.mark.timeout(timeout=600, method="thread")
    def test_options_call_with_path_setup_with_any_implicit_api(self):
        """
        Options Request to a path that was defined as ANY in SAM through AWS::Serverless::Function Events
        """
        response = requests.options(self.url + "/anyandall")

        self.assertEqual(response.status_code, 200)

    @pytest.mark.timeout(timeout=600, method="thread")
    def test_patch_call_with_path_setup_with_any_implicit_api(self):
        """
        Patch Request to a path that was defined as ANY in SAM through AWS::Serverless::Function Events
        """
        response = requests.patch(self.url + "/anyandall")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"hello": "world"})


class TestStartApiWithSwaggerApis(StartApiIntegBaseClass):
    template_path = "/testdata/start_api/swagger-template.yaml"
    binary_data_file = "testdata/start_api/binarydata.gif"

    def setUp(self):
        self.url = "http://127.0.0.1:{}".format(self.port)

    @pytest.mark.timeout(timeout=600, method="thread")
    def test_get_call_with_path_setup_with_any_swagger(self):
        """
        Get Request to a path that was defined as ANY in SAM through Swagger
        """
        response = requests.get(self.url + "/anyandall")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"hello": "world"})

    @pytest.mark.timeout(timeout=600, method="thread")
    def test_post_call_with_path_setup_with_any_swagger(self):
        """
        Post Request to a path that was defined as ANY in SAM through Swagger
        """
        response = requests.post(self.url + "/anyandall", json={})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"hello": "world"})

    @pytest.mark.timeout(timeout=600, method="thread")
    def test_put_call_with_path_setup_with_any_swagger(self):
        """
        Put Request to a path that was defined as ANY in SAM through Swagger
        """
        response = requests.put(self.url + "/anyandall", json={})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"hello": "world"})

    @pytest.mark.timeout(timeout=600, method="thread")
    def test_head_call_with_path_setup_with_any_swagger(self):
        """
        Head Request to a path that was defined as ANY in SAM through Swagger
        """
        response = requests.head(self.url + "/anyandall")

        self.assertEqual(response.status_code, 200)

    @pytest.mark.timeout(timeout=600, method="thread")
    def test_delete_call_with_path_setup_with_any_swagger(self):
        """
        Delete Request to a path that was defined as ANY in SAM through Swagger
        """
        response = requests.delete(self.url + "/anyandall")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"hello": "world"})

    @pytest.mark.timeout(timeout=600, method="thread")
    def test_options_call_with_path_setup_with_any_swagger(self):
        """
        Options Request to a path that was defined as ANY in SAM through Swagger
        """
        response = requests.options(self.url + "/anyandall")

        self.assertEqual(response.status_code, 200)

    @pytest.mark.timeout(timeout=600, method="thread")
    def test_patch_call_with_path_setup_with_any_swagger(self):
        """
        Patch Request to a path that was defined as ANY in SAM through Swagger
        """
        response = requests.patch(self.url + "/anyandall")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"hello": "world"})

    @pytest.mark.timeout(timeout=600, method="thread")
    def test_function_not_defined_in_template(self):
        response = requests.get(self.url + "/nofunctionfound")

        self.assertEqual(response.status_code, 502)
        self.assertEqual(response.json(), {"message": "No function defined for resource method"})

    @pytest.mark.timeout(timeout=600, method="thread")
    def test_function_with_no_api_event_is_reachable(self):
        response = requests.get(self.url + "/functionwithnoapievent")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"hello": "world"})

    @pytest.mark.timeout(timeout=600, method="thread")
    def test_lambda_function_resource_is_reachable(self):
        response = requests.get(self.url + "/nonserverlessfunction")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"hello": "world"})

    @pytest.mark.timeout(timeout=600, method="thread")
    def test_binary_request(self):
        """
        This tests that the service can accept and invoke a lambda when given binary data in a request
        """
        input_data = self.get_binary_data(self.binary_data_file)
        response = requests.post(
            self.url + "/echobase64eventbody", headers={"Content-Type": "image/gif"}, data=input_data
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers.get("Content-Type"), "image/gif")
        self.assertEqual(response.content, input_data)

    @pytest.mark.timeout(timeout=600, method="thread")
    def test_binary_response(self):
        """
        Binary data is returned correctly
        """
        expected = self.get_binary_data(self.binary_data_file)

        response = requests.get(self.url + "/base64response")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers.get("Content-Type"), "image/gif")
        self.assertEqual(response.content, expected)


class TestStartApiWithSwaggerRestApis(StartApiIntegBaseClass):
    template_path = "/testdata/start_api/swagger-rest-api-template.yaml"
    binary_data_file = "testdata/start_api/binarydata.gif"

    def setUp(self):
        self.url = "http://127.0.0.1:{}".format(self.port)

    @pytest.mark.timeout(timeout=600, method="thread")
    def test_get_call_with_path_setup_with_any_swagger(self):
        """
        Get Request to a path that was defined as ANY in SAM through Swagger
        """
        response = requests.get(self.url + "/anyandall")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"hello": "world"})

    @pytest.mark.timeout(timeout=600, method="thread")
    def test_post_call_with_path_setup_with_any_swagger(self):
        """
        Post Request to a path that was defined as ANY in SAM through Swagger
        """
        response = requests.post(self.url + "/anyandall", json={})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"hello": "world"})

    @pytest.mark.timeout(timeout=600, method="thread")
    def test_put_call_with_path_setup_with_any_swagger(self):
        """
        Put Request to a path that was defined as ANY in SAM through Swagger
        """
        response = requests.put(self.url + "/anyandall", json={})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"hello": "world"})

    @pytest.mark.timeout(timeout=600, method="thread")
    def test_head_call_with_path_setup_with_any_swagger(self):
        """
        Head Request to a path that was defined as ANY in SAM through Swagger
        """
        response = requests.head(self.url + "/anyandall")

        self.assertEqual(response.status_code, 200)

    @pytest.mark.timeout(timeout=600, method="thread")
    def test_delete_call_with_path_setup_with_any_swagger(self):
        """
        Delete Request to a path that was defined as ANY in SAM through Swagger
        """
        response = requests.delete(self.url + "/anyandall")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"hello": "world"})

    @pytest.mark.timeout(timeout=600, method="thread")
    def test_options_call_with_path_setup_with_any_swagger(self):
        """
        Options Request to a path that was defined as ANY in SAM through Swagger
        """
        response = requests.options(self.url + "/anyandall")

        self.assertEqual(response.status_code, 200)

    @pytest.mark.timeout(timeout=600, method="thread")
    def test_patch_call_with_path_setup_with_any_swagger(self):
        """
        Patch Request to a path that was defined as ANY in SAM through Swagger
        """
        response = requests.patch(self.url + "/anyandall")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"hello": "world"})

    @pytest.mark.timeout(timeout=600, method="thread")
    def test_function_not_defined_in_template(self):
        response = requests.get(self.url + "/nofunctionfound")

        self.assertEqual(response.status_code, 502)
        self.assertEqual(response.json(), {"message": "No function defined for resource method"})

    @pytest.mark.timeout(timeout=600, method="thread")
    def test_lambda_function_resource_is_reachable(self):
        response = requests.get(self.url + "/nonserverlessfunction")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"hello": "world"})

    @pytest.mark.timeout(timeout=600, method="thread")
    def test_binary_request(self):
        """
        This tests that the service can accept and invoke a lambda when given binary data in a request
        """
        input_data = self.get_binary_data(self.binary_data_file)
        response = requests.post(
            self.url + "/echobase64eventbody", headers={"Content-Type": "image/gif"}, data=input_data
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers.get("Content-Type"), "image/gif")
        self.assertEqual(response.content, input_data)

    @pytest.mark.timeout(timeout=600, method="thread")
    def test_binary_response(self):
        """
        Binary data is returned correctly
        """
        expected = self.get_binary_data(self.binary_data_file)

        response = requests.get(self.url + "/base64response")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers.get("Content-Type"), "image/gif")
        self.assertEqual(response.content, expected)


class TestServiceResponses(StartApiIntegBaseClass):
    """
    Test Class centered around the different responses that can happen in Lambda and pass through start-api
    """

    template_path = "/testdata/start_api/template.yaml"
    binary_data_file = "testdata/start_api/binarydata.gif"

    def setUp(self):
        self.url = "http://127.0.0.1:{}".format(self.port)

    @pytest.mark.timeout(timeout=600, method="thread")
    def test_multiple_headers_response(self):
        response = requests.get(self.url + "/multipleheaders")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers.get("Content-Type"), "text/plain")
        self.assertEqual(response.headers.get("MyCustomHeader"), "Value1, Value2")

    @pytest.mark.timeout(timeout=600, method="thread")
    def test_multiple_headers_overrides_headers_response(self):
        response = requests.get(self.url + "/multipleheadersoverridesheaders")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers.get("Content-Type"), "text/plain")
        self.assertEqual(response.headers.get("MyCustomHeader"), "Value1, Value2, Custom")

    @pytest.mark.timeout(timeout=600, method="thread")
    def test_binary_response(self):
        """
        Binary data is returned correctly
        """
        expected = self.get_binary_data(self.binary_data_file)

        response = requests.get(self.url + "/base64response")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers.get("Content-Type"), "image/gif")
        self.assertEqual(response.content, expected)

    @pytest.mark.timeout(timeout=600, method="thread")
    def test_default_header_content_type(self):
        """
        Test that if no ContentType is given the default is "application/json"
        """
        response = requests.get(self.url + "/onlysetstatuscode")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content.decode("utf-8"), "no data")
        self.assertEqual(response.headers.get("Content-Type"), "application/json")

    @pytest.mark.timeout(timeout=600, method="thread")
    def test_default_status_code(self):
        """
        Test that if no status_code is given, the status code is 200
        :return:
        """
        response = requests.get(self.url + "/onlysetbody")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"hello": "world"})

    @pytest.mark.timeout(timeout=600, method="thread")
    def test_string_status_code(self):
        """
        Test that an integer-string can be returned as the status code
        """
        response = requests.get(self.url + "/stringstatuscode")

        self.assertEqual(response.status_code, 200)

    @pytest.mark.timeout(timeout=600, method="thread")
    def test_default_body(self):
        """
        Test that if no body is given, the response is 'no data'
        """
        response = requests.get(self.url + "/onlysetstatuscode")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content.decode("utf-8"), "no data")

    @pytest.mark.timeout(timeout=600, method="thread")
    def test_function_writing_to_stdout(self):
        response = requests.get(self.url + "/writetostdout")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"hello": "world"})

    @pytest.mark.timeout(timeout=600, method="thread")
    def test_function_writing_to_stderr(self):
        response = requests.get(self.url + "/writetostderr")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"hello": "world"})

    @pytest.mark.timeout(timeout=600, method="thread")
    def test_integer_body(self):
        response = requests.get(self.url + "/echo_integer_body")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content.decode("utf-8"), "42")


class TestServiceRequests(StartApiIntegBaseClass):
    """
    Test Class centered around the different requests that can happen
    """

    template_path = "/testdata/start_api/template.yaml"
    binary_data_file = "testdata/start_api/binarydata.gif"

    def setUp(self):
        self.url = "http://127.0.0.1:{}".format(self.port)

    @pytest.mark.timeout(timeout=600, method="thread")
    def test_binary_request(self):
        """
        This tests that the service can accept and invoke a lambda when given binary data in a request
        """
        input_data = self.get_binary_data(self.binary_data_file)
        response = requests.post(
            self.url + "/echobase64eventbody", headers={"Content-Type": "image/gif"}, data=input_data
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers.get("Content-Type"), "image/gif")
        self.assertEqual(response.content, input_data)

    @pytest.mark.timeout(timeout=600, method="thread")
    def test_request_with_form_data(self):
        """
        Form-encoded data should be put into the Event to Lambda
        """
        response = requests.post(
            self.url + "/echoeventbody", headers={"Content-Type": "application/x-www-form-urlencoded"}, data="key=value"
        )

        self.assertEqual(response.status_code, 200)

        response_data = response.json()

        self.assertEqual(response_data.get("headers").get("Content-Type"), "application/x-www-form-urlencoded")
        self.assertEqual(response_data.get("body"), "key=value")

    @pytest.mark.timeout(timeout=600, method="thread")
    def test_request_to_an_endpoint_with_two_different_handlers(self):
        response = requests.get(self.url + "/echoeventbody")

        self.assertEqual(response.status_code, 200)

        response_data = response.json()

        self.assertEqual(response_data.get("handler"), "echo_event_handler_2")

    @pytest.mark.timeout(timeout=600, method="thread")
    def test_request_with_multi_value_headers(self):
        response = requests.get(
            self.url + "/echoeventbody", headers={"Content-Type": "application/x-www-form-urlencoded, image/gif"}
        )

        self.assertEqual(response.status_code, 200)
        response_data = response.json()
        self.assertEqual(
            response_data.get("multiValueHeaders").get("Content-Type"), ["application/x-www-form-urlencoded, image/gif"]
        )
        self.assertEqual(
            response_data.get("headers").get("Content-Type"), "application/x-www-form-urlencoded, image/gif"
        )

    @pytest.mark.timeout(timeout=600, method="thread")
    def test_request_with_query_params(self):
        """
        Query params given should be put into the Event to Lambda
        """
        response = requests.get(self.url + "/id/4", params={"key": "value"})

        self.assertEqual(response.status_code, 200)

        response_data = response.json()

        self.assertEqual(response_data.get("queryStringParameters"), {"key": "value"})
        self.assertEqual(response_data.get("multiValueQueryStringParameters"), {"key": ["value"]})

    @pytest.mark.timeout(timeout=600, method="thread")
    def test_request_with_list_of_query_params(self):
        """
        Query params given should be put into the Event to Lambda
        """
        response = requests.get(self.url + "/id/4", params={"key": ["value", "value2"]})

        self.assertEqual(response.status_code, 200)

        response_data = response.json()

        self.assertEqual(response_data.get("queryStringParameters"), {"key": "value2"})
        self.assertEqual(response_data.get("multiValueQueryStringParameters"), {"key": ["value", "value2"]})

    @pytest.mark.timeout(timeout=600, method="thread")
    def test_request_with_path_params(self):
        """
        Path Parameters given should be put into the Event to Lambda
        """
        response = requests.get(self.url + "/id/4")

        self.assertEqual(response.status_code, 200)

        response_data = response.json()

        self.assertEqual(response_data.get("pathParameters"), {"id": "4"})

    @pytest.mark.timeout(timeout=600, method="thread")
    def test_request_with_many_path_params(self):
        """
        Path Parameters given should be put into the Event to Lambda
        """
        response = requests.get(self.url + "/id/4/user/jacob")

        self.assertEqual(response.status_code, 200)

        response_data = response.json()

        self.assertEqual(response_data.get("pathParameters"), {"id": "4", "user": "jacob"})

    @pytest.mark.timeout(timeout=600, method="thread")
    def test_forward_headers_are_added_to_event(self):
        """
        Test the Forwarding Headers exist in the Api Event to Lambda
        """
        response = requests.get(self.url + "/id/4")

        response_data = response.json()

        self.assertEqual(response_data.get("headers").get("X-Forwarded-Proto"), "http")
        self.assertEqual(response_data.get("multiValueHeaders").get("X-Forwarded-Proto"), ["http"])
        self.assertEqual(response_data.get("headers").get("X-Forwarded-Port"), self.port)
        self.assertEqual(response_data.get("multiValueHeaders").get("X-Forwarded-Port"), [self.port])


class TestStartApiWithStage(StartApiIntegBaseClass):
    """
    Test Class centered around the different responses that can happen in Lambda and pass through start-api
    """

    template_path = "/testdata/start_api/template.yaml"

    def setUp(self):
        self.url = "http://127.0.0.1:{}".format(self.port)

    @pytest.mark.timeout(timeout=600, method="thread")
    def test_default_stage_name(self):
        response = requests.get(self.url + "/echoeventbody")

        self.assertEqual(response.status_code, 200)

        response_data = response.json()

        self.assertEqual(response_data.get("requestContext", {}).get("stage"), "Prod")

    @pytest.mark.timeout(timeout=600, method="thread")
    def test_global_stage_variables(self):
        response = requests.get(self.url + "/echoeventbody")

        self.assertEqual(response.status_code, 200)

        response_data = response.json()

        self.assertEqual(response_data.get("stageVariables"), {"VarName": "varValue"})


class TestStartApiWithStageAndSwagger(StartApiIntegBaseClass):
    """
    Test Class centered around the different responses that can happen in Lambda and pass through start-api
    """

    template_path = "/testdata/start_api/swagger-template.yaml"

    def setUp(self):
        self.url = "http://127.0.0.1:{}".format(self.port)

    @pytest.mark.timeout(timeout=600, method="thread")
    def test_swagger_stage_name(self):
        response = requests.get(self.url + "/echoeventbody")

        self.assertEqual(response.status_code, 200)

        response_data = response.json()
        self.assertEqual(response_data.get("requestContext", {}).get("stage"), "dev")

    @pytest.mark.timeout(timeout=600, method="thread")
    def test_swagger_stage_variable(self):
        response = requests.get(self.url + "/echoeventbody")

        self.assertEqual(response.status_code, 200)

        response_data = response.json()
        self.assertEqual(response_data.get("stageVariables"), {"VarName": "varValue"})


class TestServiceCorsSwaggerRequests(StartApiIntegBaseClass):
    """
    Test to check that the correct headers are being added with Cors with swagger code
    """

    template_path = "/testdata/start_api/swagger-template.yaml"
    binary_data_file = "testdata/start_api/binarydata.gif"

    def setUp(self):
        self.url = "http://127.0.0.1:{}".format(self.port)

    @pytest.mark.timeout(timeout=600, method="thread")
    def test_cors_swagger_options(self):
        """
        This tests that the Cors are added to option requests in the swagger template
        """
        response = requests.options(self.url + "/echobase64eventbody")

        self.assertEqual(response.status_code, 200)

        self.assertEqual(response.headers.get("Access-Control-Allow-Origin"), "*")
        self.assertEqual(response.headers.get("Access-Control-Allow-Headers"), "origin, x-requested-with")
        self.assertEqual(response.headers.get("Access-Control-Allow-Methods"), "GET,OPTIONS")
        self.assertEqual(response.headers.get("Access-Control-Max-Age"), "510")


class TestServiceCorsGlobalRequests(StartApiIntegBaseClass):
    """
    Test to check that the correct headers are being added with Cors with the global property
    """

    template_path = "/testdata/start_api/template.yaml"

    def setUp(self):
        self.url = "http://127.0.0.1:{}".format(self.port)

    @pytest.mark.timeout(timeout=600, method="thread")
    def test_cors_global(self):
        """
        This tests that the Cors are added to options requests when the global property is set
        """
        response = requests.options(self.url + "/echobase64eventbody")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers.get("Access-Control-Allow-Origin"), "*")
        self.assertEqual(response.headers.get("Access-Control-Allow-Headers"), None)
        self.assertEqual(response.headers.get("Access-Control-Allow-Methods"), ",".join(sorted(Route.ANY_HTTP_METHODS)))
        self.assertEqual(response.headers.get("Access-Control-Max-Age"), None)

    @pytest.mark.timeout(timeout=600, method="thread")
    def test_cors_global_get(self):
        """
        This tests that the Cors are added to post requests when the global property is set
        """
        response = requests.get(self.url + "/onlysetstatuscode")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content.decode("utf-8"), "no data")
        self.assertEqual(response.headers.get("Content-Type"), "application/json")
        self.assertEqual(response.headers.get("Access-Control-Allow-Origin"), None)
        self.assertEqual(response.headers.get("Access-Control-Allow-Headers"), None)
        self.assertEqual(response.headers.get("Access-Control-Allow-Methods"), None)
        self.assertEqual(response.headers.get("Access-Control-Max-Age"), None)


class TestStartApiWithCloudFormationStage(StartApiIntegBaseClass):
    """
    Test Class centered around the different responses that can happen in Lambda and pass through start-api
    """

    template_path = "/testdata/start_api/swagger-rest-api-template.yaml"

    def setUp(self):
        self.url = "http://127.0.0.1:{}".format(self.port)

    @pytest.mark.timeout(timeout=600, method="thread")
    def test_default_stage_name(self):
        response = requests.get(self.url + "/echoeventbody")

        self.assertEqual(response.status_code, 200)

        response_data = response.json()
        self.assertEqual(response_data.get("requestContext", {}).get("stage"), "Dev")

    @pytest.mark.timeout(timeout=600, method="thread")
    def test_global_stage_variables(self):
        response = requests.get(self.url + "/echoeventbody")

        self.assertEqual(response.status_code, 200)

        response_data = response.json()

        self.assertEqual(response_data.get("stageVariables"), {"Stack": "Dev"})


class TestStartApiWithMethodsAndResources(StartApiIntegBaseClass):
    template_path = "/testdata/start_api/methods-resources-api-template.yaml"
    binary_data_file = "testdata/start_api/binarydata.gif"

    def setUp(self):
        self.url = "http://127.0.0.1:{}".format(self.port)

    @pytest.mark.timeout(timeout=600, method="thread")
    def test_get_call_with_path_setup_with_any_swagger(self):
        """
        Get Request to a path that was defined as ANY in SAM through Swagger
        """
        response = requests.get(self.url + "/root/anyandall")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"hello": "world"})

    @pytest.mark.timeout(timeout=600, method="thread")
    def test_post_call_with_path_setup_with_any_swagger(self):
        """
        Post Request to a path that was defined as ANY in SAM through Swagger
        """
        response = requests.post(self.url + "/root/anyandall", json={})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"hello": "world"})

    @pytest.mark.timeout(timeout=600, method="thread")
    def test_put_call_with_path_setup_with_any_swagger(self):
        """
        Put Request to a path that was defined as ANY in SAM through Swagger
        """
        response = requests.put(self.url + "/root/anyandall", json={})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"hello": "world"})

    @pytest.mark.timeout(timeout=600, method="thread")
    def test_head_call_with_path_setup_with_any_swagger(self):
        """
        Head Request to a path that was defined as ANY in SAM through Swagger
        """
        response = requests.head(self.url + "/root/anyandall")

        self.assertEqual(response.status_code, 200)

    @pytest.mark.timeout(timeout=600, method="thread")
    def test_delete_call_with_path_setup_with_any_swagger(self):
        """
        Delete Request to a path that was defined as ANY in SAM through Swagger
        """
        response = requests.delete(self.url + "/root/anyandall")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"hello": "world"})

    @pytest.mark.timeout(timeout=600, method="thread")
    def test_options_call_with_path_setup_with_any_swagger(self):
        """
        Options Request to a path that was defined as ANY in SAM through Swagger
        """
        response = requests.options(self.url + "/root/anyandall")

        self.assertEqual(response.status_code, 200)

    @pytest.mark.timeout(timeout=600, method="thread")
    def test_patch_call_with_path_setup_with_any_swagger(self):
        """
        Patch Request to a path that was defined as ANY in SAM through Swagger
        """
        response = requests.patch(self.url + "/root/anyandall")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"hello": "world"})

    @pytest.mark.timeout(timeout=600, method="thread")
    def test_function_not_defined_in_template(self):
        response = requests.get(self.url + "/root/nofunctionfound")

        self.assertEqual(response.status_code, 502)
        self.assertEqual(response.json(), {"message": "No function defined for resource method"})

    @pytest.mark.timeout(timeout=600, method="thread")
    def test_lambda_function_resource_is_reachable(self):
        response = requests.get(self.url + "/root/nonserverlessfunction")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"hello": "world"})

    @pytest.mark.timeout(timeout=600, method="thread")
    def test_binary_request(self):
        """
        This tests that the service can accept and invoke a lambda when given binary data in a request
        """
        input_data = self.get_binary_data(self.binary_data_file)
        response = requests.post(
            self.url + "/root/echobase64eventbody", headers={"Content-Type": "image/gif"}, data=input_data
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers.get("Content-Type"), "image/gif")
        self.assertEqual(response.content, input_data)

    @pytest.mark.timeout(timeout=600, method="thread")
    def test_binary_response(self):
        """
        Binary data is returned correctly
        """
        expected = self.get_binary_data(self.binary_data_file)

        response = requests.get(self.url + "/root/base64response")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers.get("Content-Type"), "image/gif")
        self.assertEqual(response.content, expected)

    @pytest.mark.timeout(timeout=600, method="thread")
    def test_proxy_response(self):
        """
        Binary data is returned correctly
        """
        response = requests.get(self.url + "/root/v1/test")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"hello": "world"})


class TestCDKApiGateway(StartApiIntegBaseClass):
    template_path = "/testdata/start_api/cdk-sample-output.yaml"

    def setUp(self):
        self.url = "http://127.0.0.1:{}".format(self.port)

    @pytest.mark.timeout(timeout=600, method="thread")
    def test_get_with_cdk(self):
        """
        Get Request to a path that was defined as ANY in SAM through Swagger
        """
        response = requests.get(self.url + "/hello-world")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"hello": "world"})


class TestServerlessApiGateway(StartApiIntegBaseClass):
    template_path = "/testdata/start_api/serverless-sample-output.yaml"

    def setUp(self):
        self.url = "http://127.0.0.1:{}".format(self.port)

    @pytest.mark.timeout(timeout=600, method="thread")
    def test_get_with_serverless(self):
        """
        Get Request to a path that was defined as ANY in SAM through Swagger
        """
        response = requests.get(self.url + "/hello-world")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"hello": "world"})
