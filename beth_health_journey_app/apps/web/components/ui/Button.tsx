import React from 'react';

export interface ButtonProps {
  variant?: 'primary' | 'secondary' | 'outline' | 'text';
  size?: 'sm' | 'md' | 'lg';
  isFullWidth?: boolean;
  isDisabled?: boolean;
  isLoading?: boolean;
  children: React.ReactNode;
  onClick?: () => void;
}

const Button: React.FC<ButtonProps> = ({
  variant = 'primary',
  size = 'md',
  isFullWidth = false,
  isDisabled = false,
  isLoading = false,
  children,
  onClick,
  ...props
}) => {
  // Style based on variant
  const variantStyles = {
    primary: 'bg-blue-600 hover:bg-blue-700 text-white',
    secondary: 'bg-gray-200 hover:bg-gray-300 text-gray-800',
    outline: 'bg-transparent border border-blue-600 text-blue-600 hover:bg-blue-50',
    text: 'bg-transparent text-blue-600 hover:underline hover:bg-blue-50',
  };

  // Style based on size
  const sizeStyles = {
    sm: 'py-1 px-3 text-sm',
    md: 'py-2 px-4 text-base',
    lg: 'py-3 px-6 text-lg',
  };

  // Combined styles
  const buttonClass = `
    ${variantStyles[variant]}
    ${sizeStyles[size]} 
    ${isFullWidth ? 'w-full' : ''}
    rounded-md font-medium focus:outline-none focus:ring-2 focus:ring-blue-300
    transition duration-200 ease-in-out
    ${isDisabled ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}
  `;

  return (
    <button
      className={buttonClass}
      disabled={isDisabled || isLoading}
      onClick={onClick}
      {...props}
    >
      {isLoading ? (
        <div className="flex items-center justify-center">
          <svg
            className="animate-spin -ml-1 mr-2 h-4 w-4 text-current"
            xmlns="http://www.w3.org/2000/svg"
            fill="none"
            viewBox="0 0 24 24"
          >
            <circle
              className="opacity-25"
              cx="12"
              cy="12"
              r="10"
              stroke="currentColor"
              strokeWidth="4"
            ></circle>
            <path
              className="opacity-75"
              fill="currentColor"
              d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
            ></path>
          </svg>
          <span>{children}</span>
        </div>
      ) : (
        children
      )}
    </button>
  );
};

export default Button; 