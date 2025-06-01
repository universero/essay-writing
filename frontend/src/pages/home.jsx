import React from "react";
import { useNavigate } from "react-router-dom";
import { Button } from "/src/component/button.jsx";

export default function HomePage() {
    const navigate = useNavigate();

    const handleModeClick = (mode) => {
        if (mode === "pro") {
            navigate("/pro");
        } else if (mode === "test") {
            navigate("/test");
        }
    };

    return (
        <div className="h-full w-3/5 mx-auto flex flex-col items-center justify-center bg-gradient-to-tr from-gray-100  to-gray-50">
            <h1 className="text-4xl md:text-5xl font-extrabold mb-12 gradient-text">
                Essay-Writing 作文批改系统
            </h1>

            <div className="flex flex-col space-y-6 w-64">
                <Button
                    style="w-full py-4 text-lg rounded-2xl bg-gradient-to-r from-[#CAC9F0] to-[#B08EEC] hover:opacity-85 text-white"
                    onClick={() => handleModeClick("pro")}
                >
                    正式模式
                </Button>
                <Button
                    style="w-full py-4 text-lg rounded-2xl bg-gradient-to-r from-[#D1DFFB] to-[#4E87F2] hover:opacity-90 text-white"
                    onClick={() => handleModeClick("test")}
                >
                    测试模式
                </Button>
            </div>
        </div>
    );
}
