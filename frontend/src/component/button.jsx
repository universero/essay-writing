export function Button({ children, onClick ,style}) {
    const base = "px-4 py-2 rounded text-sm font-medium";
    return (
        <button onClick={onClick} className={`${base} ${style}`}>
            {children}
        </button>
    );
}