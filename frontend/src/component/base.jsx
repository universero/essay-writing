const BaseURL = "http://127.0.0.1:5000"

export default BaseURL


export const Call = async ({
                               url = "",
                               method = 'GET',
                               body = null,
                               params = null,
                               headers = {}
                           }) => {
    try {
        // 处理查询参数
        let fullUrl = url;
        if (params) {
            const queryString = new URLSearchParams(params).toString();
            fullUrl += `?${queryString}`;
        }

        // 设置默认请求头
        const defaultHeaders = {
            'Content-Type': 'application/json',
        };

        // 准备请求配置
        const config = {
            method,
            headers: {...defaultHeaders, ...headers},
            credentials: 'include' // 如果需要携带cookie
        };

        // 添加请求体（如果是GET/HEAD方法则不添加）
        if (body && !['GET', 'HEAD'].includes(method.toUpperCase())) {
            config.body = JSON.stringify(body);
        }

        // 发起请求
        const response = await fetch(fullUrl, config);

        // 检查响应状态
        if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            throw new Error(
                errorData.message || `请求失败: ${response.status} ${response.statusText}`
            );
        }

        // 解析响应数据
        const responseData = await response.json();

        // 返回payload字段，如果没有payload则返回整个响应数据
        return responseData.payload || responseData;

    } catch (error) {
        console.error('API调用错误:', error);
        throw error; // 继续抛出错误以便调用者处理
    }
};

export const Post = (url, {
    body = null,
    headers = {}
}) => {
    return Call({
        url,
        method: 'POST',
        body,
        headers
    });
};