import React from 'react';

const TextDisplay = ({ title, content }) => {
    return (
        <div className="max-w-3xl mx-auto bg-white rounded-xl shadow-lg p-8 mt-6">
            <h2 className="text-2xl font-bold text-indigo-600 mb-6 border-b pb-2">
                📄 OCR识别结果
            </h2>
            <div className="space-y-6">
                <div>
                    <h3 className="text-lg font-semibold text-gray-800 mb-2">📌 标题</h3>
                    <div className="bg-gray-100 p-4 rounded-lg border border-gray-300 text-gray-900">
                        {title || <span className="text-gray-500 italic">无标题</span>}
                    </div>
                </div>
                <div>
                    <h3 className="text-lg font-semibold text-gray-800 mb-2">📝 正文内容</h3>
                    <div className="bg-gray-100 p-4 rounded-lg border border-gray-300 text-gray-900 whitespace-pre-line leading-relaxed">
                        {content || <span className="text-gray-500 italic">无内容</span>}
                    </div>
                </div>
            </div>
        </div>
    );
};

export default TextDisplay;
