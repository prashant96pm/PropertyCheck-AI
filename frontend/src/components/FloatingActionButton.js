import React from 'react';
import { Link } from 'react-router-dom';
import { FileSearch } from 'lucide-react';

const FloatingActionButton = ({ onClick, to }) => {
  const ButtonContent = () => (
    <>
      <FileSearch className="h-7 w-7 text-white" />
      <span className="absolute -top-12 left-1/2 -translate-x-1/2 whitespace-nowrap px-3 py-1.5 rounded-lg text-sm font-medium bg-slate-800 text-white opacity-0 group-hover:opacity-100 transition-opacity duration-200 shadow-lg">
        Scan Document
      </span>
    </>
  );
  
  if (to) {
    return (
      <Link to={to} className="fab group">
        <ButtonContent />
      </Link>
    );
  }
  
  return (
    <button onClick={onClick} className="fab group">
      <ButtonContent />
    </button>
  );
};

export default FloatingActionButton;
