import React, { useState, useRef, useCallback } from 'react';
import { parametersService } from '../../services/parameters';

const ParameterAutocomplete = ({ 
  value, 
  onChange, 
  onParameterSelect,
  placeholder = "Type @@ to see parameters...",
  className = ""
}) => {
  const [suggestions, setSuggestions] = useState([]);
  const [showSuggestions, setShowSuggestions] = useState(false);
  const [selectedIndex, setSelectedIndex] = useState(-1);
  const inputRef = useRef(null);
  const suggestionsRef = useRef(null);
  const timeoutRef = useRef(null);

  const fetchSuggestions = useCallback(async (term) => {
    try {
      const response = await parametersService.getAutocomplete(term);
      
      // Always update suggestions from server for comprehensive results
      const filteredSuggestions = term && term.length > 0 
        ? response.suggestions.filter(suggestion =>
            suggestion.value.toLowerCase().includes(term.toLowerCase())
          )
        : response.suggestions;
      
      setSuggestions(filteredSuggestions);
      setShowSuggestions(filteredSuggestions.length > 0);
      setSelectedIndex(-1); // Reset selection when suggestions change
    } catch (error) {
      console.error('Failed to fetch parameter suggestions:', error);
      setSuggestions([]);
      setShowSuggestions(false);
      setSelectedIndex(-1);
    }
  }, []);

  const debouncedFetchSuggestions = useCallback((term) => {
    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current);
    }
    
    timeoutRef.current = setTimeout(() => {
      fetchSuggestions(term);
    }, 150); // 150ms debounce
  }, [fetchSuggestions]);

  const handleInputChange = (e) => {
    const newValue = e.target.value;
    const position = e.target.selectionStart;
    
    onChange(newValue);
    
    // Check if user typed @@
    const textBeforeCursor = newValue.substring(0, position);
    const lastAtAt = textBeforeCursor.lastIndexOf('@@');
    
    if (lastAtAt !== -1) {
      // Check if we're still typing a parameter
      const textAfterAtAt = textBeforeCursor.substring(lastAtAt + 2);
      const hasSpaceOrSpecialChar = /[\s\n\r,;.!?()]/.test(textAfterAtAt);
      
      if (!hasSpaceOrSpecialChar) {
        // Filter suggestions as user types with debouncing
        const currentSearch = textAfterAtAt.toLowerCase();
        
        // If we already have suggestions, filter them locally for instant feedback
        if (suggestions.length > 0) {
          const filteredSuggestions = suggestions.filter(suggestion =>
            suggestion.value.toLowerCase().includes(currentSearch)
          );
          setSuggestions(filteredSuggestions);
          setShowSuggestions(filteredSuggestions.length > 0);
          setSelectedIndex(-1);
        }
        
        // Also fetch from server with debouncing for comprehensive results
        debouncedFetchSuggestions(currentSearch);
        return;
      }
    }
    
    // Hide suggestions when not in parameter context
    setShowSuggestions(false);
    setSelectedIndex(-1);
  };

  const selectParameter = useCallback((parameter) => {
    const position = inputRef.current?.selectionStart || 0;
    const textBeforeCursor = value.substring(0, position);
    const textAfterCursor = value.substring(position);
    const lastAtAt = textBeforeCursor.lastIndexOf('@@');
    
    if (lastAtAt !== -1) {
      const beforeParameter = value.substring(0, lastAtAt);
      const newValue = beforeParameter + '@@' + parameter.value + textAfterCursor;
      const newCursorPosition = lastAtAt + parameter.value.length + 2;
      
      onChange(newValue);
      setShowSuggestions(false);
      setSelectedIndex(-1);
      
      // Set cursor position after parameter
      setTimeout(() => {
        if (inputRef.current) {
          inputRef.current.setSelectionRange(newCursorPosition, newCursorPosition);
          inputRef.current.focus();
        }
      }, 0);
      
      if (onParameterSelect) {
        onParameterSelect(parameter);
      }
    }
  }, [value, onChange, onParameterSelect]);

  const handleKeyDown = (e) => {
    if (!showSuggestions || suggestions.length === 0) {
      return;
    }

    switch (e.key) {
      case 'ArrowDown':
        e.preventDefault();
        setSelectedIndex(prev => {
          const nextIndex = prev < suggestions.length - 1 ? prev + 1 : 0;
          scrollToSelectedItem(nextIndex);
          return nextIndex;
        });
        break;
        
      case 'ArrowUp':
        e.preventDefault();
        setSelectedIndex(prev => {
          const nextIndex = prev > 0 ? prev - 1 : suggestions.length - 1;
          scrollToSelectedItem(nextIndex);
          return nextIndex;
        });
        break;
        
      case 'Enter':
        e.preventDefault();
        if (selectedIndex >= 0 && selectedIndex < suggestions.length) {
          selectParameter(suggestions[selectedIndex]);
        }
        break;
        
      case 'Escape':
        e.preventDefault();
        setShowSuggestions(false);
        setSelectedIndex(-1);
        break;
        
      case 'Tab':
        if (selectedIndex >= 0 && selectedIndex < suggestions.length) {
          e.preventDefault();
          selectParameter(suggestions[selectedIndex]);
        }
        break;
        
      default:
        break;
    }
  };

  const scrollToSelectedItem = (index) => {
    if (suggestionsRef.current) {
      const selectedElement = suggestionsRef.current.children[index + 1]; // +1 for header
      if (selectedElement) {
        selectedElement.scrollIntoView({
          block: 'nearest',
          behavior: 'smooth'
        });
      }
    }
  };

  const handleBlur = (e) => {
    // Delay hiding suggestions to allow clicking on them
    setTimeout(() => {
      setShowSuggestions(false);
      setSelectedIndex(-1);
    }, 200);
  };

  const handleSuggestionClick = (suggestion) => {
    selectParameter(suggestion);
  };

  const handleSuggestionMouseEnter = (index) => {
    setSelectedIndex(index);
  };

  return (
    <div className="relative">
      <textarea
        ref={inputRef}
        value={value}
        onChange={handleInputChange}
        onKeyDown={handleKeyDown}
        onBlur={handleBlur}
        placeholder={placeholder}
        className={`${className} font-mono`}
        rows={6}
      />
      
      {showSuggestions && suggestions.length > 0 && (
        <div 
          ref={suggestionsRef}
          className="absolute z-50 mt-1 bg-white border border-gray-300 rounded-md shadow-lg max-h-48 overflow-y-auto"
          style={{ 
            minWidth: '250px',
            top: '100%'
          }}
        >
          <div className="p-2 text-xs text-gray-600 border-b">
            Parameter suggestions (↑↓ to navigate, Enter to select):
          </div>
          {suggestions.map((suggestion, index) => (
            <div
              key={suggestion.value}
              onClick={() => handleSuggestionClick(suggestion)}
              onMouseEnter={() => handleSuggestionMouseEnter(index)}
              className={`px-3 py-2 cursor-pointer border-b border-gray-100 last:border-b-0 ${
                selectedIndex === index 
                  ? 'bg-blue-100 text-blue-900' 
                  : 'hover:bg-gray-100'
              }`}
            >
              <div className="font-medium text-blue-600">@@{suggestion.value}</div>
              {suggestion.description && (
                <div className="text-sm text-gray-600">{suggestion.description}</div>
              )}
              <div className="text-xs text-gray-500">Type: {suggestion.dataType}</div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default ParameterAutocomplete;