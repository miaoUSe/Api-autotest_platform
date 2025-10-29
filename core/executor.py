import requests
import json
import re
from typing import Dict, Any, Optional, List
from jsonpath_ng.ext import parse
from requests.exceptions import Timeout, RequestException


def send_request(
    method: str, 
    url: str, 
    headers: Optional[Dict[str, str]] = None, 
    body: Optional[Dict[str, Any]] = None,
    timeout: int = 10
) -> Dict[str, Any]:
    """
    发送HTTP请求并处理异常
    
    Args:
        method: HTTP方法 (GET, POST, PUT, DELETE等)
        url: 请求的URL
        headers: 请求头字典
        body: 请求体字典
        timeout: 超时时间(秒)
    
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
            timeout=timeout
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