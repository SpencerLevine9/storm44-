import { forwardRef, useId } from 'react';
import './Input.css';

/**
 * Input component with iOS-like styling
 * Supports: text, email, password, search, url, tel, number
 */
const Input = forwardRef(({
  type = 'text',
  size = 'md',
  label,
  helperText,
  error,
  disabled = false,
  fullWidth = false,
  leftIcon,
  rightIcon,
  className = '',
  id: providedId,
  ...props
}, ref) => {
  const generatedId = useId();
  const id = providedId || generatedId;
  const helperId = `${id}-helper`;
  const errorId = `${id}-error`;

  const wrapperClasses = [
    'input-wrapper',
    `input-wrapper--${size}`,
    fullWidth && 'input-wrapper--full-width',
    error && 'input-wrapper--error',
    disabled && 'input-wrapper--disabled',
    className
  ].filter(Boolean).join(' ');

  return (
    <div className={wrapperClasses}>
      {label && (
        <label htmlFor={id} className="input-label">
          {label}
        </label>
      )}
      <div className="input-container">
        {leftIcon && (
          <span className="input-icon input-icon--left" aria-hidden="true">
            {leftIcon}
          </span>
        )}
        <input
          ref={ref}
          type={type}
          id={id}
          className="input-field"
          disabled={disabled}
          aria-invalid={error ? 'true' : 'false'}
          aria-describedby={error ? errorId : helperText ? helperId : undefined}
          {...props}
        />
        {rightIcon && (
          <span className="input-icon input-icon--right" aria-hidden="true">
            {rightIcon}
          </span>
        )}
      </div>
      {error && (
        <span id={errorId} className="input-error" role="alert">
          {error}
        </span>
      )}
      {helperText && !error && (
        <span id={helperId} className="input-helper">
          {helperText}
        </span>
      )}
    </div>
  );
});

Input.displayName = 'Input';

export default Input;
