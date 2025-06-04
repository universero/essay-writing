import React from 'react';

const TextDisplay = ({ title, content }) => {
    return (
        <div className="bg-white rounded-lg shadow-md p-6">
            <h3 className="text-xl font-semibold mb-4">OCR识别结果</h3>
            <div className="space-y-4">
                <div>
                    <h4 className="text-lg font-medium text-gray-700 mb-2">标题</h4>
                    <div className="bg-gray-50 p-4 rounded border border-gray-200">
                        {title || '无标题'}
                    </div>
                </div>
                <div>
                    <h4 className="text-lg font-medium text-gray-700 mb-2">正文内容</h4>
                    <div className="bg-gray-50 p-4 rounded border border-gray-200 whitespace-pre-line">
                        {content || '无内容'}
                    </div>
                </div>
            </div>
        </div>
    );
};

export default TextDisplay;