import React, { useState, useEffect } from 'react';

const TextDisplay = ({ title: initialTitle, content: initialContent, onResultsChange }) => {
    // 内部状态
    const [title, setTitle] = useState(initialTitle);
    const [content, setContent] = useState(initialContent);
    const [isEditingTitle, setIsEditingTitle] = useState(false);
    const [isEditingContent, setIsEditingContent] = useState(false);

    // 当外部props变化时，同步到内部状态
    useEffect(() => {
        setTitle(initialTitle);
        setContent(initialContent);
    }, [initialTitle, initialContent]);

    // 处理标题保存
    const handleTitleSave = () => {
        setIsEditingTitle(false);
        onResultsChange({ title, content });
    };

    // 处理内容保存
    const handleContentSave = () => {
        setIsEditingContent(false);
        onResultsChange({ title, content });
    };

    // 实时同步内容变化（如果需要实时同步）
    // 或者只在保存时同步（如上方的handleTitleSave/handleContentSave）
    useEffect(() => {
        // 如果需要实时同步，取消下面这行的注释
        // onResultsChange({ title, content });
    }, [title, content]);

    return (
        <div className="max-w-3xl mx-auto bg-gradient-to-br from-white to-indigo-50 rounded-2xl shadow-xl overflow-hidden p-0 mt-8 border border-indigo-100 transition-all hover:shadow-2xl hover:-translate-y-1">
            {/* 标题区域 */}
            <div className="bg-gradient-to-r from-indigo-500 to-purple-600 p-6">
                <div className="flex items-center">
                    <div className="bg-white/20 p-3 rounded-full backdrop-blur-sm">
                        <svg xmlns="http://www.w3.org/2000/svg" className="h-8 w-8 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                        </svg>
                    </div>
                    <h2 className="ml-4 text-2xl font-bold text-white">
                        OCR识别结果
                    </h2>
                </div>
            </div>

            {/* 内容区域 */}
            <div className="p-8 space-y-8">
                <div className="transform transition-all hover:scale-[1.01]">
                    <div className="flex justify-between items-center mb-3">
                        <h3 className="text-lg font-semibold text-gray-700 flex items-center">
              <span className="bg-indigo-100 text-indigo-600 p-2 rounded-full mr-3">
                <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 8h10M7 12h4m1 8l-4-4H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-3l-4 4z" />
                </svg>
              </span>
                            标题
                        </h3>
                        {!isEditingTitle ? (
                            <button
                                onClick={() => setIsEditingTitle(true)}
                                className="text-sm text-indigo-600 hover:text-indigo-800"
                            >
                                编辑
                            </button>
                        ) : (
                            <button
                                onClick={handleTitleSave}
                                className="text-sm text-green-600 hover:text-green-800"
                            >
                                保存
                            </button>
                        )}
                    </div>

                    {isEditingTitle ? (
                        <input
                            type="text"
                            value={title}
                            onChange={(e) => setTitle(e.target.value)}
                            className="w-full bg-white p-5 rounded-xl border border-indigo-100 shadow-sm text-gray-800 font-medium text-lg transition-all hover:bg-indigo-50 hover:border-indigo-200"
                            autoFocus
                        />
                    ) : (
                        <div className="bg-white p-5 rounded-xl border border-indigo-100 shadow-sm text-gray-800 font-medium text-lg transition-all hover:bg-indigo-50 hover:border-indigo-200">
                            {title || <span className="text-gray-400 italic">无标题</span>}
                        </div>
                    )}
                </div>

                <div className="transform transition-all hover:scale-[1.01]">
                    <div className="flex justify-between items-center mb-3">
                        <h3 className="text-lg font-semibold text-gray-700 flex items-center">
              <span className="bg-indigo-100 text-indigo-600 p-2 rounded-full mr-3">
                <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 20H5a2 2 0 01-2-2V6a2 2 0 012-2h10a2 2 0 012 2v1m2 13a2 2 0 01-2-2V7m2 13a2 2 0 002-2V9a2 2 0 00-2-2h-2m-4-3H9M7 16h6M7 8h6v4H7V8z" />
                </svg>
              </span>
                            正文内容
                        </h3>
                        {!isEditingContent ? (
                            <button
                                onClick={() => setIsEditingContent(true)}
                                className="text-sm text-indigo-600 hover:text-indigo-800"
                            >
                                编辑
                            </button>
                        ) : (
                            <button
                                onClick={handleContentSave}
                                className="text-sm text-green-600 hover:text-green-800"
                            >
                                保存
                            </button>
                        )}
                    </div>

                    {isEditingContent ? (
                        <textarea
                            value={content}
                            onChange={(e) => setContent(e.target.value)}
                            className="w-full bg-white p-5 rounded-xl border border-indigo-100 shadow-sm text-gray-700 leading-relaxed font-serif transition-all hover:bg-indigo-50 hover:border-indigo-200 min-h-[200px]"
                            autoFocus
                        />
                    ) : (
                        <div className="bg-white p-5 rounded-xl border border-indigo-100 shadow-sm text-gray-700 whitespace-pre-line leading-relaxed font-serif transition-all hover:bg-indigo-50 hover:border-indigo-200">
                            {content ? (
                                <div className="space-y-4">
                                    {content.split('\n').map((paragraph, index) => (
                                        <p key={index} className="text-justify indent-8">
                                            {paragraph}
                                        </p>
                                    ))}
                                </div>
                            ) : (
                                <span className="text-gray-400 italic">无内容</span>
                            )}
                        </div>
                    )}
                </div>
            </div>

            {/* 底部装饰 */}
            <div className="bg-gradient-to-r from-indigo-100 to-purple-100 h-2 w-full"></div>
        </div>
    );
};

export default TextDisplay;