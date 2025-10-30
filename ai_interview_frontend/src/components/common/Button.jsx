import React from 'react';

const Button = ({ children, onClick, type = 'button', disabled = false }) => {
  return (
    <button
      type={type}
      onClick={onClick}
      disabled={disabled}
      className={`w-full py-3 px-4 border-none rounded-xl shadow-lg 
        text-base font-bold text-white 
        bg-gradient-to-r from-blue-500 to-cyan-500
        hover:from-blue-600 hover:to-cyan-600 
        focus:outline-none focus:ring-4 focus:ring-blue-300 focus:ring-offset-2 
        transition-all duration-300 transform hover:scale-[1.01] active:scale-[0.99]
        ${disabled ? 'opacity-60 cursor-not-allowed shadow-none' : ''}
      `}
    >
      {children}
    </button>
  );
};

export default Button;