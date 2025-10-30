import React from 'react';

const FeatureIcon = ({ icon, title }) => {
  return (
    <div className="flex flex-col items-center text-center p-3">
      <div className="text-blue-500 mb-2">{icon}</div> 
      <p className="text-sm font-semibold text-gray-700">{title}</p>
    </div>
  );
};

export default FeatureIcon;