import React, { useState, useCallback } from 'react';
import { useForm } from 'react-hook-form';
import { templatesService } from '../../services/templates';
import { formFieldsService } from '../../services/formFields';
import { parametersService } from '../../services/parameters';
import ParameterAutocomplete from '../common/ParameterAutocomplete';
import DynamicDropdown from '../forms/DynamicDropdown';

const TemplateForm = ({ applicationName, template, onClose, onSuccess }) => {
  const isEditing = !!template;
  const [parameterValidation, setParameterValidation] = useState({ isValid: true, errors: [] });
  const [formConfig, setFormConfig] = useState([]);
  const [isLoading, setIsLoading] = useState(false);

  const { register, handleSubmit, formState: { errors }, setValue, watch } = useForm({
    defaultValues: {
      templateName: template?.templateName || '',
      ssgTeam: template?.ssgTeam || '',
      recipientType: template?.recipientType || '',
      sender: template?.sender || '',
      subject: template?.subject || '',
      body: template?.body || '',
      autoSend: template?.autoSend || false,
      dataAsAttachment: template?.dataAsAttachment || false,
      ...template // Spread any additional fields from template
    },
  });

  // Watch subject and body for parameter validation
  const subject = watch('subject');
  const body = watch('body');

  // Validate parameters without useEffect - use callback approach
  const validateParameters = useCallback(async (text) => {
    if (!text || (!text.includes('@@'))) {
      setParameterValidation({ isValid: true, errors: [] });
      return;
    }

    try {
      const result = await parametersService.validateParameters(text);
      setParameterValidation({
        isValid: result.isValid,
        errors: result.invalidParameters || []
      });
    } catch (error) {
      console.error('Parameter validation failed:', error);
      setParameterValidation({ isValid: true, errors: [] }); // Fail silently
    }
  }, []);

  // Debounced validation - triggered by input changes
  const handleSubjectChange = useCallback((value) => {
    setValue('subject', value);
    validateParameters(`${value} ${body}`);
  }, [setValue, body, validateParameters]);

  const handleBodyChange = useCallback((value) => {
    setValue('body', value);
    validateParameters(`${subject} ${value}`);
  }, [setValue, subject, validateParameters]);

  const onSubmit = async (data) => {
    if (!parameterValidation.isValid) {
      alert('Please fix parameter validation errors before submitting');
      return;
    }
    
    setIsLoading(true);
    try {
      if (isEditing) {
        await templatesService.updateTemplate(applicationName, template.id, data);
      } else {
        await templatesService.createTemplate(applicationName, data);
      }
      
      if (onSuccess) {
        onSuccess();
      }
      onClose();
    } catch (error) {
      const message = error.response?.data?.error || `Failed to ${isEditing ? 'update' : 'create'} template`;
      alert(message);
    } finally {
      setIsLoading(false);
    }
  };

  // Helper to get dynamic field configuration
  const getFieldConfig = (fieldName) => {
    return formConfig.find(config => config.fieldName === fieldName);
  };

  // Helper to render dynamic form field
  const renderDynamicField = (fieldName) => {
    const config = getFieldConfig(fieldName);
    if (!config) return null;

    const currentValue = watch(fieldName) || '';
    const fieldError = errors[fieldName]?.message;

    return (
      <DynamicDropdown
        key={fieldName}
        field={config}
        value={currentValue}
        onChange={(value) => setValue(fieldName, value)}
        error={fieldError}
        disabled={isLoading}
      />
    );
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
      <div className="bg-white rounded-lg shadow-xl max-w-4xl w-full max-h-screen overflow-y-auto">
        <div className="p-6">
          <div className="flex justify-between items-center mb-6">
            <h2 className="text-xl font-semibold">
              {isEditing ? 'Edit Template' : 'Create Template'}
            </h2>
            <button
              onClick={onClose}
              className="text-gray-500 hover:text-gray-700"
              disabled={isLoading}
            >
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>

          <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {/* Template Name */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Template Name <span className="text-red-500">*</span>
                </label>
                <input
                  {...register('templateName', { required: 'Template name is required' })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  disabled={isLoading}
                />
                {errors.templateName && (
                  <p className="mt-1 text-sm text-red-600">{errors.templateName.message}</p>
                )}
              </div>

              {/* Dynamic SSG Team Field */}
              {renderDynamicField('ssgTeam')}
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {/* Dynamic Recipient Type Field */}
              {renderDynamicField('recipientType')}

              {/* Dynamic Sender Field */}
              {renderDynamicField('sender') || (
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Sender <span className="text-red-500">*</span>
                  </label>
                  <input
                    {...register('sender', { 
                      required: 'Sender is required',
                      pattern: {
                        value: /^[^\s@]+@[^\s@]+\.[^\s@]+$/,
                        message: 'Please enter a valid email address'
                      }
                    })}
                    type="email"
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    disabled={isLoading}
                  />
                  {errors.sender && (
                    <p className="mt-1 text-sm text-red-600">{errors.sender.message}</p>
                  )}
                </div>
              )}
            </div>

            {/* Subject with Parameter Autocomplete */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Subject <span className="text-red-500">*</span>
              </label>
              <ParameterAutocomplete
                value={subject}
                onChange={handleSubjectChange}
                placeholder="Enter email subject... (Type @@ for parameters)"
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 min-h-[40px] resize-none"
              />
              {errors.subject && (
                <p className="mt-1 text-sm text-red-600">{errors.subject.message}</p>
              )}
            </div>

            {/* Body with Parameter Autocomplete */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Body <span className="text-red-500">*</span>
              </label>
              <ParameterAutocomplete
                value={body}
                onChange={handleBodyChange}
                placeholder="Enter email body... (Type @@ for parameters)"
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
              {errors.body && (
                <p className="mt-1 text-sm text-red-600">{errors.body.message}</p>
              )}
            </div>

            {/* Parameter Validation Display */}
            {!parameterValidation.isValid && parameterValidation.errors.length > 0 && (
              <div className="bg-red-50 border border-red-200 rounded-md p-3">
                <div className="flex">
                  <div className="flex-shrink-0">
                    <svg className="h-5 w-5 text-red-400" viewBox="0 0 20 20" fill="currentColor">
                      <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                    </svg>
                  </div>
                  <div className="ml-3">
                    <h3 className="text-sm font-medium text-red-800">Invalid Parameters Found</h3>
                    <div className="mt-2 text-sm text-red-700">
                      <p>The following parameters are not valid:</p>
                      <ul className="mt-1 list-disc list-inside">
                        {parameterValidation.errors.map((param, index) => (
                          <li key={index}>@@{param}</li>
                        ))}
                      </ul>
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* Options */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="flex items-center">
                <input
                  {...register('autoSend')}
                  type="checkbox"
                  className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                  disabled={isLoading}
                />
                <label className="ml-2 block text-sm text-gray-900">
                  Enable Auto Send
                </label>
              </div>

              <div className="flex items-center">
                <input
                  {...register('dataAsAttachment')}
                  type="checkbox"
                  className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                  disabled={isLoading}
                />
                <label className="ml-2 block text-sm text-gray-900">
                  Include Data as Attachment
                </label>
              </div>
            </div>

            {/* Render any additional dynamic fields */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {formConfig
                .filter(config => !['ssgTeam', 'recipientType', 'sender'].includes(config.fieldName))
                .map(config => (
                  <div key={config.fieldName}>
                    {renderDynamicField(config.fieldName)}
                  </div>
                ))}
            </div>

            {/* Form Actions */}
            <div className="flex justify-end space-x-3 pt-6 border-t border-gray-200">
              <button
                type="button"
                onClick={onClose}
                className="px-4 py-2 text-gray-700 bg-gray-100 hover:bg-gray-200 rounded-md disabled:opacity-50"
                disabled={isLoading}
              >
                Cancel
              </button>
              <button
                type="submit"
                className="px-4 py-2 bg-blue-600 text-white hover:bg-blue-700 rounded-md disabled:opacity-50"
                disabled={isLoading || !parameterValidation.isValid}
              >
                {isLoading ? 'Saving...' : (isEditing ? 'Update Template' : 'Create Template')}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
};

export default TemplateForm;