import { forwardRef, useId } from 'react';
import './TextArea.css';

/**
 * TextArea component with iOS-like styling
 */
const TextArea = forwardRef(({
  label,
  helperText,
  error,
  disabled = false,
  fullWidth = false,
  rows = 4,
  resize = 'vertical',
  className = '',
  id: providedId,
  ...props
}, ref) => {
  const generatedId = useId();
  const id = providedId || generatedId;
  const helperId = `${id}-helper`;
  const errorId = `${id}-error`;

  const wrapperClasses = [
    'textarea-wrapper',
    fullWidth && 'textarea-wrapper--full-width',
    error && 'textarea-wrapper--error',
    disabled && 'textarea-wrapper--disabled',
    className
  ].filter(Boolean).join(' ');

  return (
    <div className={wrapperClasses}>
      {label && (
        <label htmlFor={id} className="textarea-label">
          {label}
        </label>
      )}
      <textarea
        ref={ref}
        id={id}
        className="textarea-field"
        rows={rows}
        disabled={disabled}
        style={{ resize }}
        aria-invalid={error ? 'true' : 'false'}
        aria-describedby={error ? errorId : helperText ? helperId : undefined}
        {...props}
      />
      {error && (
        <span id={errorId} className="textarea-error" role="alert">
          {error}
        </span>
      )}
      {helperText && !error && (
        <span id={helperId} className="textarea-helper">
          {helperText}
        </span>
      )}
    </div>
  );
});

TextArea.displayName = 'TextArea';

export default TextArea;
