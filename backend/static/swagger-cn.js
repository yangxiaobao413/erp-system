// Swagger UI 中文翻译脚本
(function () {
  const CN = {
    // 顶部导航
    "Select a spec": "选择API定义",
    // 接口分组
    "default": "默认",
    // 搜索
    "Search": "搜索",
    "Filter by tag": "按标签筛选",
    // 接口操作
    "GET": "获取",
    "POST": "创建",
    "PUT": "更新",
    "DELETE": "删除",
    "PATCH": "补丁",
    "HEAD": "头请求",
    "OPTIONS": "选项",
    // 按钮
    "Try it out": "试用",
    "Cancel": "取消",
    "Execute": "执行",
    "Clear": "清除",
    "Close": "关闭",
    "Download": "下载",
    "Authorize": "授权",
    // 请求/响应
    "Request URL": "请求地址",
    "Request body": "请求体",
    "Server response": "服务器响应",
    "Response body": "响应体",
    "Response headers": "响应头",
    "Responses": "响应",
    "Code": "状态码",
    "Description": "描述",
    "Links": "链接",
    "Media type": "媒体类型",
    "Example Value": "示例值",
    "Schema": "数据结构",
    // 参数
    "Parameters": "参数",
    "No parameters": "无参数",
    "Parameter content type": "参数内容类型",
    "Send empty value": "发送空值",
    // 模型
    "Schemas": "数据模型",
    "Models": "模型",
    "Model": "模型",
    "Example": "示例",
    "No Content": "无内容",
    // 其他
    "Send Request": "发送请求",
    "Available authorizations": "可用授权方式",
    "Available authorization": "可用授权",
    "Show/Hide": "显示/隐藏",
    "List Operations": "列出接口",
    "Expand Operations": "展开接口",
    "Raw": "原始",
    "Collapse": "折叠",
    "Expand": "展开",
    "Deprecated": "已弃用",
    "required": "必填",
    "string": "字符串",
    "integer": "整数",
    "number": "数字",
    "boolean": "布尔值",
    "array": "数组",
    "object": "对象",
    "none": "无",
    "Loading...": "加载中...",
    "Fetch error": "获取失败",
    "Undocumented": "未记录",
    "Curl": "Curl命令",
    "Request URL": "请求地址",
    "Server": "服务器",
    "Responses": "响应结果",
    "No operations tagged with": "没有找到标签为",
    "Operations": "接口列表",
    "Base URL": "基础地址",
    "API documentation": "API 文档",
    "Please authenticate with your API key.": "请使用您的 API 密钥进行认证。",
    "api key": "API 密钥",
    "http": "HTTP",
    "OAuth2": "OAuth2",
    "Value": "值",
  };

  const observer = new MutationObserver(function () {
    document.querySelectorAll("*").forEach(function (el) {
      // 遍历所有文本节点
      const walker = document.createTreeWalker(el, NodeFilter.SHOW_TEXT, null, false);
      let node;
      while ((node = walker.nextNode())) {
        const text = node.textContent.trim();
        if (CN[text] && text.length > 1) {
          node.textContent = node.textContent.replace(text, CN[text]);
        }
      }
      // 翻译 placeholder
      if (el.placeholder && CN[el.placeholder]) {
        el.placeholder = CN[el.placeholder];
      }
      // 翻译 aria-label
      if (el.getAttribute("aria-label") && CN[el.getAttribute("aria-label")]) {
        el.setAttribute("aria-label", CN[el.getAttribute("aria-label")]);
      }
      // 翻译 title
      if (el.title && CN[el.title]) {
        el.title = CN[el.title];
      }
    });
  });

  observer.observe(document.body, { childList: true, subtree: true, characterData: true });

  // 初始翻译
  document.addEventListener("DOMContentLoaded", function () {
    setTimeout(function () {
      document.querySelectorAll("*").forEach(function (el) {
        const walker = document.createTreeWalker(el, NodeFilter.SHOW_TEXT, null, false);
        let node;
        while ((node = walker.nextNode())) {
          const text = node.textContent.trim();
          if (CN[text] && text.length > 1) {
            node.textContent = node.textContent.replace(text, CN[text]);
          }
        }
        if (el.placeholder && CN[el.placeholder]) {
          el.placeholder = CN[el.placeholder];
        }
        if (el.getAttribute("aria-label") && CN[el.getAttribute("aria-label")]) {
          el.setAttribute("aria-label", CN[el.getAttribute("aria-label")]);
        }
        if (el.title && CN[el.title]) {
          el.title = CN[el.title];
        }
      });
    }, 500);
  });
})();
