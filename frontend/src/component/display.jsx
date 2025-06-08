import React, {useState} from 'react';
import {TransformWrapper, TransformComponent} from 'react-zoom-pan-pinch';

const ImageDisplay = ({images}) => {
    const [currentIndex, setCurrentIndex] = useState(0);

    const goToPrev = () => {
        setCurrentIndex(prevIndex =>
            prevIndex === 0 ? images.length - 1 : prevIndex - 1
        );
    };

    const goToNext = () => {
        setCurrentIndex(prevIndex =>
            prevIndex === images.length - 1 ? 0 : prevIndex + 1
        );
    };

    const goToImage = (index) => {
        setCurrentIndex(index);
    };

    return (
        <div className="bg-white h-full rounded-lg shadow-md p-6 max-w-4xl mx-auto">
            <div className="relative">
                {/* 图片展示区域 - 使用专业缩放库 */}
                <div className="border rounded-lg overflow-hidden mb-4 flex justify-center items-center"
                     style={{
                         maxHeight: '70vh',
                         minHeight: '200px'
                     }}>
                    <TransformWrapper
                        initialScale={1}
                        minScale={0.5}
                        maxScale={3}
                        wheel={{step: 0.1}}
                        doubleClick={{step: 0.5}}
                        panning={{
                            disabled: false, // 启用拖拽
                            velocityDisabled: false,
                            lockAxisX: false,
                            lockAxisY: false
                        }}
                        limitToBounds={false} // 允许拖出边界
                    >
                        {({zoomIn, zoomOut, resetTransform, ...rest}) => (
                            <>
                                {/* 缩放控制按钮 */}
                                <div className="absolute right-2 top-2 z-10 flex space-x-2">
                                    <button
                                        onClick={() => zoomIn()}
                                        className="bg-black bg-opacity-50 text-white p-2 rounded-full hover:bg-opacity-70 transition-all"
                                        aria-label="放大"
                                    >
                                        <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" fill="none"
                                             viewBox="0 0 24 24" stroke="currentColor">
                                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
                                                  d="M12 6v6m0 0v6m0-6h6m-6 0H6"/>
                                        </svg>
                                    </button>
                                    <button
                                        onClick={() => zoomOut()}
                                        className="bg-black bg-opacity-50 text-white p-2 rounded-full hover:bg-opacity-70 transition-all"
                                        aria-label="缩小"
                                    >
                                        <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" fill="none"
                                             viewBox="0 0 24 24" stroke="currentColor">
                                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
                                                  d="M20 12H4"/>
                                        </svg>
                                    </button>
                                    <button
                                        onClick={() => resetTransform()}
                                        className="bg-black bg-opacity-50 text-white p-2 rounded-full hover:bg-opacity-70 transition-all"
                                        aria-label="重置"
                                    >
                                        <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" fill="none"
                                             viewBox="0 0 24 24" stroke="currentColor">
                                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
                                                  d="M4 8V4m0 0h4M4 4l5 5m11-1V4m0 0h-4m4 0l-5 5M4 16v4m0 0h4m-4 0l5-5m11 5l-5-5m5 5v-4m0 4h-4"/>
                                        </svg>
                                    </button>
                                </div>

                                <TransformComponent
                                    wrapperStyle={{
                                        width: "100%",
                                        height: "100%",
                                        display: "flex",
                                        justifyContent: "center",
                                        alignItems: "center"
                                    }}
                                    contentStyle={{
                                        width: "100%",
                                        height: "100%",
                                        display: "flex",
                                        justifyContent: "center",
                                        alignItems: "center"
                                    }}
                                >
                                    <img
                                        src={`data:image/jpeg;base64,${images[currentIndex].image}`}
                                        alt={`图片 ${currentIndex + 1}`}
                                        style={{
                                            maxWidth: "100%",
                                            maxHeight: "100%",
                                            objectFit: "contain",
                                            display: "block"
                                        }}
                                    />
                                </TransformComponent>
                            </>
                        )}
                    </TransformWrapper>
                </div>

                {/* 导航箭头 */}
                {images.length > 1 && (
                    <>
                        <button
                            onClick={goToPrev}
                            className="absolute left-0 top-1/2 -translate-y-1/2 bg-black bg-opacity-50 text-white p-2 rounded-full hover:bg-opacity-70 transition-all z-10"
                            aria-label="上一张"
                        >
                            <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24"
                                 stroke="currentColor">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7"/>
                            </svg>
                        </button>
                        <button
                            onClick={goToNext}
                            className="absolute right-0 top-1/2 -translate-y-1/2 bg-black bg-opacity-50 text-white p-2 rounded-full hover:bg-opacity-70 transition-all z-10"
                            aria-label="下一张"
                        >
                            <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24"
                                 stroke="currentColor">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7"/>
                            </svg>
                        </button>
                    </>
                )}

                {/* 图片信息 */}
                <div className="text-center text-gray-600 mb-2">
                    图片 {currentIndex + 1} / {images.length}
                </div>

                {/* 指示点 */}
                {images.length > 1 && (
                    <div className="flex justify-center space-x-2">
                        {images.map((_, index) => (
                            <button
                                key={index}
                                onClick={() => goToImage(index)}
                                className={`w-3 h-3 rounded-full transition-all ${index === currentIndex ? 'bg-blue-500' : 'bg-gray-300'}`}
                                aria-label={`跳转到图片 ${index + 1}`}
                            />
                        ))}
                    </div>
                )}
            </div>
        </div>
    );
};

export default ImageDisplay;