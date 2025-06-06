import React, {useState, useCallback} from 'react';

const FileUpload = ({
                        uploadUrl,
                        onSuccess,
                        onError,
                        maxSize = 5,
                        accept,
                        multiple = false,
                        label = '点击或拖拽作文图片到此处上传'
                    }) => {
    const [files, setFiles] = useState([]);
    const [isDragging, setIsDragging] = useState(false);
    const [uploadProgress, setUploadProgress] = useState(0);
    const [isUploading, setIsUploading] = useState(false);

    const handleFileChange = (e) => {
        const selectedFiles = Array.from(e.target.files);
        validateAndSetFiles(selectedFiles);
    };

    const validateAndSetFiles = (fileList) => {
        const validFiles = [];
        const invalidFiles = [];

        fileList.forEach(file => {
            if (file.size > maxSize * 1024 * 1024) {
                invalidFiles.push({
                    file,
                    error: `文件大小超过${maxSize}MB限制`
                });
            } else {
                validFiles.push(file);
            }
        });

        if (invalidFiles.length > 0) {
            alert(`以下文件不符合要求:\n${invalidFiles.map(f => `${f.file.name}: ${f.error}`).join('\n')}`);
        }

        const updatedFiles = multiple ? [...files, ...validFiles] : validFiles;
        setFiles(updatedFiles);
    };

    const handleUpload = async () => {
        if (files.length === 0) return;

        setIsUploading(true);
        setUploadProgress(0);

        try {
            const formData = new FormData();

            // 将所有文件添加到formData的image字段中
            files.forEach(file => {
                formData.append('images', file); // 使用相同的字段名
            });

            const xhr = new XMLHttpRequest();

            xhr.upload.addEventListener('progress', (event) => {
                if (event.lengthComputable) {
                    const progress = Math.round((event.loaded / event.total) * 100);
                    setUploadProgress(progress);
                }
            });

            xhr.addEventListener('load', () => {
                if (xhr.status >= 200 && xhr.status < 300) {
                    setUploadProgress(100);
                    try {
                        const response = JSON.parse(xhr.responseText);
                        if (onSuccess) onSuccess(files, response.payload);
                    } catch (error) {
                        console.error('上传失败:', error);
                        if (onSuccess) onSuccess(files, []); // 如果解析失败，传递空数组
                    }
                } else {
                    throw new Error(`上传失败: ${xhr.statusText}`);
                }
            });

            xhr.addEventListener('error', () => {
                throw new Error('上传过程中发生错误');
            });

            xhr.open('POST', uploadUrl, true);
            xhr.send(formData);

        } catch (error) {
            console.error('上传失败:', error);
            if (onError) onError(error);
        } finally {
            setIsUploading(false);
        }
    };

    const handleDragEnter = useCallback((e) => {
        e.preventDefault();
        setIsDragging(true);
    }, []);

    const handleDragLeave = useCallback((e) => {
        e.preventDefault();
        setIsDragging(false);
    }, []);

    const handleDragOver = useCallback((e) => {
        e.preventDefault();
    }, []);

    const handleDrop = useCallback((e) => {
        e.preventDefault();
        setIsDragging(false);
        const droppedFiles = Array.from(e.dataTransfer.files);
        validateAndSetFiles(droppedFiles);
    }, []);

    const removeFile = (index) => {
        const updatedFiles = [...files];
        updatedFiles.splice(index, 1);
        setFiles(updatedFiles);
    };

    const clearFiles = () => {
        setFiles([]);
        setUploadProgress(0);
    };

    return (
        <div className="max-w-xl mx-auto">
            <div
                className={`border-2 border-dashed rounded-lg p-10 text-center transition-colors ${
                    isDragging
                        ? 'border-green-500 bg-green-50'
                        : 'border-gray-300 hover:border-gray-400'
                }`}
                onDragEnter={handleDragEnter}
                onDragLeave={handleDragLeave}
                onDragOver={handleDragOver}
                onDrop={handleDrop}
            >
                <input
                    type="file"
                    id="file-upload"
                    className="hidden"
                    onChange={handleFileChange}
                    accept={accept ? accept.join(',') : undefined}
                    multiple={multiple}
                />
                <label
                    htmlFor="file-upload"
                    className="cursor-pointer flex flex-col items-center justify-center space-y-2"
                >
                    <svg
                        className="w-12 h-12 text-gray-400"
                        fill="none"
                        stroke="currentColor"
                        viewBox="0 0 24 24"
                        xmlns="http://www.w3.org/2000/svg"
                    >
                        <path
                            strokeLinecap="round"
                            strokeLinejoin="round"
                            strokeWidth="2"
                            d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"
                        ></path>
                    </svg>
                    <p className="text-gray-600">{label}</p>
                    <p className="text-sm text-gray-500">
                        支持 {accept ? accept.join(', ') : '所有文件类型'}，最大 {maxSize}MB
                    </p>
                </label>
            </div>

            {files.length > 0 && (
                <div className="mt-6">
                    <div className="flex justify-between items-center mb-3">
                        <h4 className="text-lg font-medium text-gray-900">
                            已选择文件 ({files.length})
                        </h4>
                        <div className="space-x-2">
                            <button
                                onClick={clearFiles}
                                className="px-3 py-1 text-sm text-gray-600 hover:text-gray-800"
                                disabled={isUploading}
                            >
                                清空
                            </button>
                            <button
                                onClick={handleUpload}
                                className="px-3 py-1 bg-blue-500 text-white rounded hover:bg-blue-600 disabled:opacity-50"
                                disabled={isUploading}
                            >
                                {isUploading ? '上传中...' : '开始上传'}
                            </button>
                        </div>
                    </div>

                    {isUploading && (
                        <div className="mb-4">
                            <div className="w-full bg-gray-200 rounded-full h-2.5">
                                <div
                                    className="bg-green-500 h-2.5 rounded-full"
                                    style={{width: `${uploadProgress}%`}}
                                ></div>
                            </div>
                            <p className="text-sm text-gray-500 mt-1">
                                总上传进度: {uploadProgress}%
                            </p>
                        </div>
                    )}

                    <ul className="space-y-2">
                        {files.map((file, index) => (
                            <li
                                key={`${file.name}-${index}`}
                                className="border rounded-md p-3 hover:bg-gray-50 transition-colors"
                            >
                                <div className="flex justify-between items-start">
                                    <div className="flex-1 min-w-0">
                                        <p className="text-sm font-medium text-gray-900 truncate">
                                            {file.name}
                                        </p>
                                        <p className="text-xs text-gray-500">
                                            {(file.size / (1024 * 1024)).toFixed(2)} MB
                                        </p>
                                    </div>
                                    <button
                                        type="button"
                                        onClick={() => removeFile(index)}
                                        className="text-gray-400 hover:text-red-500 transition-colors"
                                        disabled={isUploading}
                                    >
                                        <svg
                                            className="w-5 h-5"
                                            fill="none"
                                            stroke="currentColor"
                                            viewBox="0 0 24 24"
                                            xmlns="http://www.w3.org/2000/svg"
                                        >
                                            <path
                                                strokeLinecap="round"
                                                strokeLinejoin="round"
                                                strokeWidth="2"
                                                d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"
                                            ></path>
                                        </svg>
                                    </button>
                                </div>
                            </li>
                        ))}
                    </ul>
                </div>
            )}
        </div>
    );
};

export default FileUpload;