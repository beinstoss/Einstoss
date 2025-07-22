import React, { useState, useMemo } from 'react';

const DynamicDropdown = ({
  field,
  value = '',
  onChange,
  error = null,
  disabled = false
}) => {
  const [isOpen, setIsOpen] = useState(false);

  // Parse selected values without useEffect
  const selectedValues = useMemo(() => {
    if (!field.allowMultiSelect) return [];
    if (!value) return [];
    return typeof value === 'string' ? value.split(',').map(v => v.trim()).filter(Boolean) : [];
  }, [value, field.allowMultiSelect]);

  const handleSingleSelect = (e) => {
    const selectedValue = e.target.value;
    onChange(selectedValue);
  };

  const handleMultiSelect = (optionValue) => {
    const currentValues = selectedValues;
    let newSelectedValues;
    
    if (currentValues.includes(optionValue)) {
      // Remove value - maintain order
      newSelectedValues = currentValues.filter(v => v !== optionValue);
    } else {
      // Add value - append to end to maintain selection order
      newSelectedValues = [...currentValues, optionValue];
    }
    
    // Build comma-delimited string in selection order
    const newValue = newSelectedValues.join(', ');
    onChange(newValue);
  };

  const handleRemoveValue = (valueToRemove) => {
    const newSelectedValues = selectedValues.filter(v => v !== valueToRemove);
    const newValue = newSelectedValues.join(', ');
    onChange(newValue);
  };

  const toggleDropdown = () => {
    if (!disabled) {
      setIsOpen(!isOpen);
    }
  };

  const handleBlur = () => {
    // Delay to allow for click events on options
    setTimeout(() => setIsOpen(false), 150);
  };

  const getDisplayValue = () => {
    if (field.allowMultiSelect) {
      return selectedValues.length > 0 ? `${selectedValues.length} selected` : 'Select options...';
    }
    
    const selectedOption = field.options.find(opt => opt.value === value);
    return selectedOption ? selectedOption.text : 'Select an option...';
  };

  const isOptionSelected = (optionValue) => {
    if (field.allowMultiSelect) {
      return selectedValues.includes(optionValue);
    }
    return value === optionValue;
  };

  if (!field.allowMultiSelect) {
    // Single select dropdown
    return (
      <div className="space-y-1">
        <label className="block text-sm font-medium text-gray-700">
          {field.fieldLabel}
          {field.isRequired && <span className="text-red-500 ml-1">*</span>}
        </label>
        <select
          value={value}
          onChange={handleSingleSelect}
          disabled={disabled}
          className={`
            w-full px-3 py-2 border rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500
            ${error ? 'border-red-500' : 'border-gray-300'}
            ${disabled ? 'bg-gray-100 cursor-not-allowed' : 'bg-white'}
          `}
        >
          <option value="">Select an option...</option>
          {field.options.map((option) => (
            <option key={option.value} value={option.value}>
              {option.text}
            </option>
          ))}
        </select>
        {error && <p className="text-sm text-red-600">{error}</p>}
      </div>
    );
  }

  // Multi-select dropdown
  return (
    <div className="space-y-1">
      <label className="block text-sm font-medium text-gray-700">
        {field.fieldLabel}
        {field.isRequired && <span className="text-red-500 ml-1">*</span>}
      </label>
      
      {/* Selected values display */}
      {selectedValues.length > 0 && (
        <div className="flex flex-wrap gap-1 mb-2">
          {selectedValues.map((selectedValue, index) => {
            const option = field.options.find(opt => opt.value === selectedValue);
            return (
              <span
                key={`${selectedValue}-${index}`}
                className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800"
              >
                {option ? option.text : selectedValue}
                <button
                  type="button"
                  onClick={() => handleRemoveValue(selectedValue)}
                  className="ml-1 inline-flex items-center justify-center w-4 h-4 rounded-full hover:bg-blue-200 focus:outline-none"
                  disabled={disabled}
                >
                  ×
                </button>
              </span>
            );
          })}
        </div>
      )}
      
      {/* Dropdown container */}
      <div className="relative">
        <button
          type="button"
          onClick={toggleDropdown}
          onBlur={handleBlur}
          disabled={disabled}
          className={`
            w-full px-3 py-2 text-left border rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500
            ${error ? 'border-red-500' : 'border-gray-300'}
            ${disabled ? 'bg-gray-100 cursor-not-allowed' : 'bg-white cursor-pointer hover:bg-gray-50'}
          `}
        >
          <span className="block truncate text-gray-700">
            {getDisplayValue()}
          </span>
          <span className="absolute inset-y-0 right-0 flex items-center pr-2 pointer-events-none">
            <svg
              className={`w-5 h-5 text-gray-400 transition-transform ${isOpen ? 'rotate-180' : ''}`}
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
            </svg>
          </span>
        </button>

        {/* Dropdown options */}
        {isOpen && (
          <div className="absolute z-10 w-full mt-1 bg-white border border-gray-300 rounded-md shadow-lg max-h-60 overflow-auto">
            {field.options.map((option) => {
              const selected = isOptionSelected(option.value);
              return (
                <div
                  key={option.value}
                  onClick={() => handleMultiSelect(option.value)}
                  className={`
                    px-3 py-2 cursor-pointer select-none hover:bg-gray-100
                    ${selected ? 'bg-blue-50 text-blue-900' : 'text-gray-900'}
                  `}
                >
                  <div className="flex items-center">
                    <input
                      type="checkbox"
                      checked={selected}
                      onChange={() => {}} // Controlled by parent click
                      className="mr-2 focus:ring-blue-500 h-4 w-4 text-blue-600 border-gray-300 rounded"
                      tabIndex={-1}
                    />
                    <span className="block truncate">{option.text}</span>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>
      
      {error && <p className="text-sm text-red-600">{error}</p>}
    </div>
  );
};

export default DynamicDropdown;