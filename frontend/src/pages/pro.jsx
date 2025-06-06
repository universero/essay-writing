import React, {useState} from "react";
import FileUpload from "/src/component/upload.jsx";
import ImageDisplay from "/src/component/display.jsx";
import TextDisplay from "/src/component/text.jsx";
import BaseURL, {Post} from "../component/base.jsx"; // 新建的文本显示组件

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
                case 'locate': {
                    const processRes = await fetchProcessResults(locateResults);
                    setProcessResults(processRes);
                    setCurrentStep('process');
                    break;
                }
                case 'process': {
                    const ocrRes = await fetchOcrResults(processResults);
                    setOcrResults(ocrRes);
                    setCurrentStep('ocr');
                    break;
                }
                case 'ocr': {
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

    const fetchProcessResults = async (locateResults) => {
        const data = {images: locateResults.map(item => item.image)};
        const resp = await Post(BaseURL + '/process', {body: data})
        return resp.map((processedImage, index) => {
            return {
                // image: processedImage,  // 使用处理后的图像 TODO
                image: locateResults[index].image,
                class: locateResults[index].class  // 保留原始分类
            };
        });
    };

    const fetchOcrResults = async (processResults) => {
        let data = {images: processResults};
        return await Post(BaseURL + '/ocr/bee', {body: data})
    };

    const fetchFinalResults = async (ocrData) => {
        console.log(ocrData);
        const result = await Post(BaseURL + '/evaluate/render', {body: ocrData});
        return [{image: result, class: 2}];
    };

    const handleUploadError = (error) => {
        console.error("上传失败：", error);
        alert(`上传失败: ${error.message || '请检查网络连接后重试'}`);
    };

    return (
        <div className="min-h-screen flex flex-col items-center bg-white p-4 pt-4">
            <h2 className="text-2xl font-bold mb-4">正式模式</h2>

            {/* 步骤指示器 */}
            <div className="flex mb-4 w-full max-w-2xl justify-center">
                {['upload', 'locate', 'process', 'ocr', 'result'].map((step, index) => (
                    <React.Fragment key={step}>
                        <div className={`flex flex-col items-center ${currentStep === step ? 'text-blue-500' : 'text-gray-400'}`}>
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

            {/* 主内容容器 - 添加 flex-grow 和 min-h-0 确保正确扩展 */}
            <div className="flex flex-col items-center w-full max-w-4xl flex-grow min-h-0">
                {/* 内容区域 - 添加 flex-grow 和 overflow-auto */}
                <div className="w-full flex-grow overflow-auto">
                    {currentStep === 'upload' && (
                        <>
                            <FileUpload
                                uploadUrl="http://localhost:5000/locate"
                                onSuccess={handleUploadSuccess}
                                onError={handleUploadError}
                                maxSize={10}
                                accept={['image/*']}
                                multiple={true}
                                className="w-full max-w-md mx-auto"
                            />
                            {uploadedFiles.length > 0 && (
                                <div className="mt-4 w-full max-w-md mx-auto">
                                    <h3 className="text-lg font-medium mb-2">已上传文件 ({uploadedFiles.length})</h3>
                                    <div className="bg-gray-50 rounded-lg p-3">
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

                    {['locate', 'process', 'result'].includes(currentStep) && (
                        <div className="h-full min-h-[400px]">
                            <ImageDisplay
                                images={currentStep === 'locate' ? locateResults :
                                    currentStep === 'process' ? processResults : finalResults}
                                title={currentStep === 'locate' ? "定位结果" :
                                    currentStep === 'process' ? "处理结果" : "最终结果"}
                                description={currentStep === 'locate' ? "这是系统识别出的定位结果图片" :
                                    currentStep === 'process' ? "这是经过处理后的图片结果" : "这是系统生成的最终结果图片"}
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

                {/* 导航按钮 - 固定在内容下方 */}
                <div className="w-full mt-2 flex-grow justify-center space-x-4">
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
        </div>
    );
}