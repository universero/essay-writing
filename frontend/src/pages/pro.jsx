import React, { useState } from "react";

export default function ProPage() {
    const [files, setFiles] = useState([]);

    const handleFileChange = (e) => {
        const selectedFiles = Array.from(e.target.files);
        setFiles(selectedFiles);
        console.log("选中的文件：", selectedFiles);
        // 可在这里添加上传逻辑，例如逐个上传
    };

    return (
        <div className="min-h-screen flex flex-col items-center justify-center bg-white p-4">
            <h2 className="text-2xl font-bold mb-6">正式模式</h2>
            <input
                type="file"
                multiple
                onChange={handleFileChange}
                className="mb-4"
            />
            {files.length > 0 && (
                <ul className="text-sm text-gray-600">
                    {files.map((file, index) => (
                        <li key={index}>已选文件：{file.name}</li>
                    ))}
                </ul>
            )}
        </div>
    );
}
