import React, {useState} from "react";
import FileUpload from "/src/component/upload.jsx";
import ImageDisplay from "/src/component/display.jsx";
import TextDisplay from "/src/component/text.jsx"; // 新建的文本显示组件

export default function ProPage() {
    // 状态管理
    const [uploadedFiles, setUploadedFiles] = useState([]);
    const [currentStep, setCurrentStep] = useState('upload'); // upload -> locate -> process -> ocr -> result
    const [locateResults, setLocateResults] = useState([]);
    const [processResults, setProcessResults] = useState([]);
    const [ocrResults, setOcrResults] = useState({title: '', content: ''});
    const [finalResults, setFinalResults] = useState([]);
    const [isLoading, setIsLoading] = useState(false);

    // 处理上传成功
    const handleUploadSuccess = async (files, results) => {
        setUploadedFiles(files);
        setLocateResults(results);
        setCurrentStep('locate');
    };

    // 处理步骤转换
    const handleNextStep = async () => {
        setIsLoading(true);
        try {
            switch (currentStep) {
                case 'locate':
                    // 调用API获取处理结果
                {
                    const processRes = await fetchProcessResults(locateResults);
                    setProcessResults(processRes);
                    setCurrentStep('process');
                    break;
                }
                case 'process':
                    // 调用API获取OCR结果
                {
                    const ocrRes = await fetchOcrResults(processResults);
                    setOcrResults(ocrRes);
                    setCurrentStep('ocr');
                    break;
                }
                case 'ocr':
                    // 调用API获取最终结果
                {
                    const finalRes = await fetchFinalResults(ocrResults);
                    setFinalResults(finalRes);
                    setCurrentStep('result');
                    break;
                }
                default:
                    break;
            }
        } catch (error) {
            console.error('步骤转换失败:', error);
            alert(`操作失败: ${error.message}`);
        } finally {
            setIsLoading(false);
        }
    };

    const handlePrevStep = () => {
        switch (currentStep) {
            case 'locate':
                setCurrentStep('upload');
                break;
            case 'process':
                setCurrentStep('locate');
                break;
            case 'ocr':
                setCurrentStep('process');
                break;
            case 'result':
                setCurrentStep('ocr');
                break;
            default:
                break;
        }
    };

    // 模拟API调用函数
    const fetchProcessResults = async (images) => {
        // 实际项目中替换为真实的API调用
        return new Promise(resolve => {
            setTimeout(() => {
                resolve(images); // 这里返回模拟数据
            }, 1000);
        });
    };

    const fetchOcrResults = async (images) => {
        return new Promise(resolve => {
            setTimeout(() => {
                resolve({
                    title: "示例标题",
                    content: "这是OCR识别出的正文内容..."
                });
            }, 1000);
        });
    };

    const fetchFinalResults = async (ocrData) => {
        return new Promise(resolve => {
            setTimeout(() => {
                resolve([/* 模拟最终图片数组 */]);
            }, 1000);
        });
    };

    const handleUploadError = (error) => {
        console.error("上传失败：", error);
        alert(`上传失败: ${error.message || '请检查网络连接后重试'}`);
    };

    return (
        <div className="min-h-screen flex flex-col items-center bg-white p-4 pt-8"> {/* 增加 pt-8 让顶部有更多空间 */}
            <h2 className="text-2xl font-bold mb-4">正式模式</h2> {/* 减少 mb-6 到 mb-4 */}

            {/* 步骤指示器 - 向上移动 */}
            <div className="flex mb-4 w-full max-w-2xl justify-center"> {/* 减少 mb-8 到 mb-4 */}
                {['upload', 'locate', 'process', 'ocr', 'result'].map((step, index) => (
                    <React.Fragment key={step}>
                        <div
                            className={`flex flex-col items-center ${currentStep === step ? 'text-blue-500' : 'text-gray-400'}`}
                        >
                            <div className={`w-8 h-8 rounded-full flex items-center justify-center 
                            ${currentStep === step ? 'bg-blue-500 text-white' :
                                index < ['upload', 'locate', 'process', 'ocr', 'result'].indexOf(currentStep) ?
                                    'bg-green-500 text-white' : 'bg-gray-200'}`}>
                                {index + 1}
                            </div>
                            <div className="mt-2 text-sm capitalize">{step}</div>
                        </div>
                        {index < 4 && (
                            <div className="flex items-start justify-center px-2">
                                <div className="w-8 h-0.5 bg-gray-300 mt-4"></div>
                            </div>
                        )}
                    </React.Fragment>
                ))}
            </div>

            {/* 内容区域 - 调整上边距 */}
            <div className="w-full max-w-4xl mt-2"> {/* 减少默认间距 */}
                {currentStep === 'upload' && (
                    <>
                        <FileUpload
                            uploadUrl="http://localhost:5000/locate"
                            onSuccess={handleUploadSuccess}
                            onError={handleUploadError}
                            maxSize={10}
                            accept={['image/*']}
                            multiple={true}
                            className="w-full max-w-md"
                        />
                        {uploadedFiles.length > 0 && (
                            <div className="mt-4 w-full max-w-md"> {/* 减少 mt-6 到 mt-4 */}
                                <h3 className="text-lg font-medium mb-2">已上传文件 ({uploadedFiles.length})</h3>
                                <div className="bg-gray-50 rounded-lg p-3"> {/* 减少 p-4 到 p-3 */}
                                    <ul className="space-y-2">
                                        {uploadedFiles.map((file, index) => (
                                            <li
                                                key={index}
                                                className="flex items-center justify-between p-2 hover:bg-gray-100 rounded transition-colors"
                                            >
                                                <div className="flex items-center min-w-0">
                                                    <svg className="w-5 h-5 text-gray-400 mr-2"></svg>
                                                    <span className="truncate flex-1">{file.name}</span>
                                                </div>
                                                <span className="text-xs text-gray-500 ml-2 whitespace-nowrap">
                                                {(file.size / (1024 * 1024)).toFixed(2)} MB
                                            </span>
                                            </li>
                                        ))}
                                    </ul>
                                </div>
                            </div>
                        )}
                    </>
                )}

                {/* 图片显示区域 - 增加高度 */}
                {['locate', 'process', 'result'].includes(currentStep) && (
                    <div className="h-[calc(100vh-280px)] min-h-[400px]"> {/* 设置固定高度 */}
                        <ImageDisplay
                            images={currentStep === 'locate' ? locateResults :
                                currentStep === 'process' ? processResults : finalResults}
                            title={currentStep === 'locate' ? "定位结果" :
                                currentStep === 'process' ? "处理结果" : "最终结果"}
                            description={currentStep === 'locate' ? "这是系统识别出的定位结果图片" :
                                currentStep === 'process' ? "这是经过处理后的图片结果" : "这是系统生成的最终结果图片"}
                            className="h-full" // 让图片容器填满父容器
                        />
                    </div>
                )}

                {currentStep === 'ocr' && (
                    <TextDisplay
                        title={ocrResults.title}
                        content={ocrResults.content}
                    />
                )}
            </div>

            {/* 导航按钮 - 向上移动 */}
            <div className="mt-6 flex space-x-4"> {/* 减少 mt-8 到 mt-6 */}
                {currentStep !== 'upload' && (
                    <button
                        onClick={handlePrevStep}
                        disabled={isLoading}
                        className="px-6 py-2 bg-gray-200 text-gray-700 rounded hover:bg-gray-300 transition-colors disabled:opacity-50"
                    >
                        上一步
                    </button>
                )}

                {currentStep !== 'result' && currentStep !== 'upload' && (
                    <button
                        onClick={handleNextStep}
                        disabled={isLoading}
                        className="px-6 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 transition-colors disabled:opacity-50"
                    >
                        {isLoading ? '处理中...' : '下一步'}
                    </button>
                )}

                {currentStep === 'result' && (
                    <button
                        onClick={() => setCurrentStep('upload')}
                        className="px-6 py-2 bg-green-500 text-white rounded hover:bg-green-600 transition-colors"
                    >
                        完成并重新开始
                    </button>
                )}
            </div>
        </div>
    );
}