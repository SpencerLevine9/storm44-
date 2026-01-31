import { forwardRef } from 'react';
import './IconButton.css';

/**
 * IconButton component for icon-only actions
 * Variants: primary, secondary, ghost, destructive
 * Sizes: sm, md, lg
 */
const IconButton = forwardRef(({
  children,
  variant = 'ghost',
  size = 'md',
  disabled = false,
  loading = false,
  label,
  className = '',
  ...props
}, ref) => {
  const classes = [
    'icon-btn',
    `icon-btn--${variant}`,
    `icon-btn--${size}`,
    loading && 'icon-btn--loading',
    className
  ].filter(Boolean).join(' ');

  return (
    <button
      ref={ref}
      type="button"
      className={classes}
      disabled={disabled || loading}
      aria-label={label}
      aria-busy={loading}
      {...props}
    >
      {loading ? (
        <span className="icon-btn__spinner" aria-hidden="true">
          <svg className="icon-btn__spinner-icon" viewBox="0 0 24 24">
            <circle
              cx="12"
              cy="12"
              r="10"
              fill="none"
              stroke="currentColor"
              strokeWidth="3"
              strokeLinecap="round"
            />
          </svg>
        </span>
      ) : (
        <span className="icon-btn__icon" aria-hidden="true">
          {children}
        </span>
      )}
    </button>
  );
});

IconButton.displayName = 'IconButton';

export default IconButton;
