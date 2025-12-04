import requests
import json
import re
from typing import Dict, Any, Optional, List
from jsonpath_ng.ext import parse
from requests.exceptions import Timeout, RequestException
from .models import TestCase, TestReport
from django.contrib.auth.models import User
from django.utils import timezone


def send_request(
    method: str, 
    url: str, 
    headers: Optional[Dict[str, str]] = None, 
    body: Optional[Dict[str, Any]] = None,
    timeout: int = 10,
    proxies: Optional[Dict[str, str]] = None
) -> Dict[str, Any]:
    """
    发送HTTP请求并处理异常
    
    Args:
        method: HTTP方法 (GET, POST, PUT, DELETE等)
        url: 请求的URL
        headers: 请求头字典
        body: 请求体字典
        timeout: 超时时间(秒)
        proxies: 代理配置字典，例如 {'http': 'http://proxy:port', 'https': 'http://proxy:port'}
                设置为 {'http': None, 'https': None} 可禁用代理
    
    Returns:
        包含请求结果的字典，包括状态码、响应时间、响应体等信息
    """
    # 初始化返回结果
    result = {
        "success": False,
        "status_code": None,
        "elapsed_time": 0,
        "response_body": None,
        "error_message": None
    }
    
    try:
        # 处理请求参数
        if headers is None:
            headers = {}
            
        # 处理请求体
        json_body = None
        if body:
            # 如果Content-Type是application/json，将body转为JSON字符串
            if 'Content-Type' in headers and headers['Content-Type'] == 'application/json':
                json_body = json.dumps(body)
            else:
                json_body = body
        
        # 发送HTTP请求
        response = requests.request(
            method=method.upper(),
            url=url,
            headers=headers,
            data=json_body if json_body else None,
            timeout=timeout,
            proxies=proxies
        )
        
        # 填充成功的结果信息
        result["success"] = True
        result["status_code"] = response.status_code
        result["elapsed_time"] = round(response.elapsed.total_seconds() * 1000, 2)  # 转换为毫秒
        
        # 尝试解析响应体为JSON
        try:
            result["response_body"] = response.json()
        except ValueError:
            # 如果不是JSON格式，则保存为文本
            result["response_body"] = response.text
            
    except Timeout:
        result["error_message"] = f"请求超时 ({timeout}秒)"
    except RequestException as e:
        result["error_message"] = f"请求异常: {str(e)}"
    except Exception as e:
        result["error_message"] = f"未知错误: {str(e)}"
        
    return result


def run_assertions(
    response_data: Dict[str, Any], 
    config_elements: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """
    根据配置元件校验请求结果
    
    Args:
        response_data: 请求返回的数据
        config_elements: 配置元件列表
    
    Returns:
        断言结果列表
    """
    assertion_results = []
    
    # 遍历配置元件，只处理类型为"assertion"的元件
    for element in config_elements:
        if element.get("type") != "assertion":
            continue
            
        # 获取断言类型和期望值
        check_type = element.get("check_type")
        expected_value = element.get("expected_value")
        json_path = element.get("json_path", "")
        
        # 初始化断言结果
        result = {
            "passed": False,
            "check_type": check_type,
            "expected": expected_value,
            "actual": None,
            "message": ""
        }
        
        try:
            if check_type == "status_code":  # 状态码断言
                actual_status = response_data.get("status_code")
                result["actual"] = actual_status
                
                # 检查状态码是否匹配
                if str(actual_status) == str(expected_value):
                    result["passed"] = True
                    result["message"] = f"状态码匹配: {actual_status}"
                else:
                    result["message"] = f"状态码不匹配. 期望: {expected_value}, 实际: {actual_status}"
                    
            elif check_type == "path_match":  # JSON路径断言
                response_body = response_data.get("response_body", {})
                
                # 使用jsonpath-ng提取值
                if json_path and response_body:
                    try:
                        jsonpath_expr = parse(json_path)
                        matches = jsonpath_expr.find(response_body)
                        
                        if matches:
                            actual_value = matches[0].value
                            result["actual"] = actual_value
                            
                            # 检查值是否匹配
                            if str(actual_value) == str(expected_value):
                                result["passed"] = True
                                result["message"] = f"路径 '{json_path}' 值匹配: {actual_value}"
                            else:
                                result["message"] = f"路径 '{json_path}' 值不匹配. 期望: {expected_value}, 实际: {actual_value}"
                        else:
                            result["message"] = f"JSON路径 '{json_path}' 未找到匹配项"
                    except Exception as e:
                        result["message"] = f"JSON路径表达式错误: {str(e)}"
                else:
                    result["message"] = "响应体为空或未提供JSON路径"
            else:
                result["message"] = f"不支持的断言类型: {check_type}"
                
        except Exception as e:
            result["message"] = f"断言执行出错: {str(e)}"
            
        assertion_results.append(result)
        
    return assertion_results


def extract_variables(
    response_data: Dict[str, Any], 
    config_elements: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    根据配置元件从响应数据中提取变量。
    
    Args:
        response_data: 请求返回的数据
        config_elements: 配置元件列表
    
    Returns:
        提取到的变量字典 {variable_name: value}
    """
    extracted_vars = {}
    
    # 遍历配置元件，只处理类型为"extraction"的元件
    for element in config_elements:
        if element.get("type") != "extraction":
            continue
            
        # 获取提取配置
        extract_method = element.get("method")  # "jsonpath" 或 "regex"
        variable_name = element.get("variable_name")
        expression = element.get("expression")
        
        if not variable_name or not expression:
            continue
            
        try:
            if extract_method == "jsonpath":
                response_body = response_data.get("response_body", {})
                if response_body and expression:
                    try:
                        jsonpath_expr = parse(expression)
                        matches = jsonpath_expr.find(response_body)
                        
                        if matches:
                            # 提取第一个匹配的值
                            extracted_value = matches[0].value
                            extracted_vars[variable_name] = extracted_value
                    except Exception as e:
                        # JSONPath 表达式错误，跳过该元素
                        pass
                        
            elif extract_method == "regex":
                response_text = response_data.get("response_body", "")
                if isinstance(response_text, dict):
                    response_text = json.dumps(response_text)
                    
                if response_text and expression:
                    try:
                        match = re.search(expression, response_text)
                        if match:
                            # 如果有捕获组，使用第一个捕获组，否则使用整个匹配
                            extracted_value = match.group(1) if match.groups() else match.group(0)
                            extracted_vars[variable_name] = extracted_value
                    except Exception as e:
                        # 正则表达式错误，跳过该元素
                        pass
        except Exception as e:
            # 其他异常，跳过该元素
            pass
            
    return extracted_vars

class TestRunner:
    def __init__(self, project_id, executor):
        """
        初始化测试运行器
        
        Args:
            project_id: 项目ID
            executor: 执行者(User对象)
        """
        self.project_id = project_id
        self.executor = executor
        self.context = {}  # 存储变量的上下文
        self.stats = {
            "total_cases": 0,
            "passed_cases": 0,
            "failed_cases": 0,
            "duration": 0.0
        }
        self.report_details = []
    
    def _replace_variables(self, data):
        """
        递归替换数据中的 ${var_name} 格式的变量。
        
        Args:
            data: 需要替换变量的数据，可以是dict、list或str
            
        Returns:
            替换变量后的数据
        """
        if isinstance(data, str):
            def replace_match(match):
                var_name = match.group(1)
                return str(self.context.get(var_name, match.group(0)))
            
            # 匹配 ${variable_name} 格式的变量
            return re.sub(r'\$\{(\w+)\}', replace_match, data)
        elif isinstance(data, dict):
            return {key: self._replace_variables(value) for key, value in data.items()}
        elif isinstance(data, list):
            return [self._replace_variables(item) for item in data]
        else:
            return data
    
    def run_case(self, testcase: TestCase, base_url: str):
        """
        执行单个用例：变量替换 -> 请求发送 -> 断言 -> 变量提取 -> 记录详情。
        
        Args:
            testcase: TestCase 对象
            base_url: 基础URL
        """
        start_time = timezone.now()
        
        # 1. 变量替换
        method = self._replace_variables(testcase.method)
        path = self._replace_variables(testcase.path)
        headers = self._replace_variables(testcase.headers)
        body = self._replace_variables(testcase.body)
        config_elements = self._replace_variables(testcase.config_elements)
        
        # 2. 构造完整 URL
        full_url = base_url.rstrip('/') + path
        
        # 3. 发送请求
        request_result = send_request(
            method=method,
            url=full_url,
            headers=headers,
            body=body,
            proxies={'http': None, 'https': None}  # 禁用代理
        )
        
        elapsed_time = (timezone.now() - start_time).total_seconds()
        
        # 4. 运行断言
        assertion_results = []
        if request_result.get('success'):
            assertion_results = run_assertions(request_result, config_elements)
        
        # 5. 变量提取
        extracted_vars = {}
        if request_result.get('success'):
            extracted_vars = extract_variables(request_result, config_elements)
            # 更新上下文
            self.context.update(extracted_vars)
        
        # 6. 更新统计信息
        self.stats["total_cases"] += 1
        if all(r.get('passed', False) for r in assertion_results) if assertion_results else True:
            self.stats["passed_cases"] += 1
        else:
            self.stats["failed_cases"] += 1
        self.stats["duration"] += elapsed_time
        
        # 7. 记录详细结果
        case_result = {
            "testcase_id": testcase.id,
            "testcase_name": testcase.name,
            "request_info": {
                "method": method,
                "url": full_url,
                "headers": headers,
                "body": body
            },
            "response_info": request_result,
            "assertion_results": assertion_results,
            "extracted_variables": extracted_vars,
            "elapsed_time": elapsed_time,
            "passed": all(r.get('passed', False) for r in assertion_results) if assertion_results else True
        }
        
        self.report_details.append(case_result)
    
    def execute(self, testcase_ids: List[int], base_url: str) -> TestReport:
        """
        批量执行用例，并保存报告。
        
        Args:
            testcase_ids: 测试用例ID列表
            base_url: 基础URL
            
        Returns:
            TestReport: 生成的测试报告对象
        """
        # 获取测试用例
        testcases = TestCase.objects.filter(id__in=testcase_ids, project_id=self.project_id)
        
        # 依次执行测试用例
        for testcase in testcases:
            self.run_case(testcase, base_url)
        
        # 创建测试报告
        report_name = f"批量执行报告-{timezone.now().strftime('%Y-%m-%d %H:%M:%S')}"
        report = TestReport.objects.create(
            project_id=self.project_id,
            name=report_name,
            executor=self.executor,
            total_cases=self.stats["total_cases"],
            passed_cases=self.stats["passed_cases"],
            failed_cases=self.stats["failed_cases"],
            duration=round(self.stats["duration"], 2),
            result_details=self.report_details
        )
        
        return report
