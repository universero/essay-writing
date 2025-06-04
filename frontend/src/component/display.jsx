import React, {useState} from 'react';

const ImageDisplay = ({images, title, description}) => {
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
        <div className="bg-white rounded-lg shadow-md p-6 max-w-4xl mx-auto">
            <h3 className="text-xl font-semibold mb-4">{title}</h3>
            {description && <p className="text-gray-600 mb-4">{description}</p>}
            <div className="relative">
                {/* 当前图片 */}
                <div className="border rounded-lg overflow-hidden mb-4">
                    <img
                        src={`data:image/jpeg;base64,${images[currentIndex]}`}
                        alt={`上传图片 ${currentIndex + 1}`}
                        className="w-full h-96 object-contain mx-auto"
                    />
                </div>

                {/* 导航箭头 */}
                {images.length > 1 && (
                    <>
                        <button
                            onClick={goToPrev}
                            className="absolute left-0 top-1/2 -translate-y-1/2 bg-black bg-opacity-50 text-white p-2 rounded-full hover:bg-opacity-70 transition-all"
                            aria-label="上一张"
                        >
                            <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24"
                                 stroke="currentColor">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7"/>
                            </svg>
                        </button>
                        <button
                            onClick={goToNext}
                            className="absolute right-0 top-1/2 -translate-y-1/2 bg-black bg-opacity-50 text-white p-2 rounded-full hover:bg-opacity-70 transition-all"
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