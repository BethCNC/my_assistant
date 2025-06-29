import React from 'react';

export type CardProps = {
  title: string;
  children: React.ReactNode;
  variant?: 'default' | 'outlined';
};

const Card = ({ 
  title, 
  children, 
  variant = 'default' 
}: CardProps) => {
  const baseStyles = 'rounded-lg p-4 shadow-md';
  
  const variantStyles = {
    default: 'bg-white border-2 border-gray-200',
    outlined: 'bg-transparent border-2 border-primary-600',
  };
  
  return (
    <div className={`${baseStyles} ${variantStyles[variant]}`}>
      <h3 className="text-lg font-medium mb-2">{title}</h3>
      <div>{children}</div>
    </div>
  );
};

export default Card; 