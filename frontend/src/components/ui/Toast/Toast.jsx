import { useState, useCallback, useRef, useEffect } from 'react';
import { createPortal } from 'react-dom';
import { X, CheckCircle, AlertCircle, AlertTriangle, Info } from 'lucide-react';
import IconButton from '../IconButton';
import { ToastContext } from './ToastContext';
import './Toast.css';

let toastId = 0;

/**
 * Toast Provider - wrap your app with this
 */
export function ToastProvider({ children, position = 'bottom-right' }) {
  const [toasts, setToasts] = useState([]);

  const addToast = useCallback((options) => {
    const id = ++toastId;
    const toast = {
      id,
      duration: 5000,
      ...options,
    };
    
    setToasts(prev => [...prev, toast]);
    
    return id;
  }, []);

  const removeToast = useCallback((id) => {
    setToasts(prev => prev.filter(toast => toast.id !== id));
  }, []);

  const toast = useCallback((message, options = {}) => {
    return addToast({ message, variant: 'default', ...options });
  }, [addToast]);

  // Add variant methods
  const toastWithVariants = Object.assign(toast, {
    success: (message, options = {}) => 
      addToast({ message, variant: 'success', ...options }),
    error: (message, options = {}) => 
      addToast({ message, variant: 'error', ...options }),
    warning: (message, options = {}) => 
      addToast({ message, variant: 'warning', ...options }),
    info: (message, options = {}) => 
      addToast({ message, variant: 'info', ...options }),
  });

  return (
    <ToastContext.Provider value={{ toast: toastWithVariants, removeToast }}>
      {children}
      {createPortal(
        <ToastContainer toasts={toasts} position={position} onRemove={removeToast} />,
        document.body
      )}
    </ToastContext.Provider>
  );
}

/**
 * Toast container
 */
function ToastContainer({ toasts, position, onRemove }) {
  return (
    <div className={`toast-container toast-container--${position}`} aria-live="polite">
      {toasts.map(toast => (
        <ToastItem key={toast.id} {...toast} onRemove={onRemove} />
      ))}
    </div>
  );
}

/**
 * Individual toast item
 */
function ToastItem({ 
  id, 
  message, 
  title,
  variant = 'default', 
  duration = 5000, 
  action,
  onRemove 
}) {
  const [isExiting, setIsExiting] = useState(false);
  const timerRef = useRef(null);

  const handleRemove = useCallback(() => {
    setIsExiting(true);
    setTimeout(() => onRemove(id), 200);
  }, [id, onRemove]);

  useEffect(() => {
    if (duration > 0) {
      timerRef.current = setTimeout(handleRemove, duration);
    }
    return () => {
      if (timerRef.current) {
        clearTimeout(timerRef.current);
      }
    };
  }, [duration, handleRemove]);

  const handleMouseEnter = () => {
    if (timerRef.current) {
      clearTimeout(timerRef.current);
    }
  };

  const handleMouseLeave = () => {
    if (duration > 0) {
      timerRef.current = setTimeout(handleRemove, duration);
    }
  };

  const Icon = {
    success: CheckCircle,
    error: AlertCircle,
    warning: AlertTriangle,
    info: Info,
    default: null,
  }[variant];

  const classes = [
    'toast',
    `toast--${variant}`,
    isExiting && 'toast--exiting'
  ].filter(Boolean).join(' ');

  return (
    <div 
      className={classes}
      role="alert"
      onMouseEnter={handleMouseEnter}
      onMouseLeave={handleMouseLeave}
    >
      {Icon && (
        <span className="toast__icon">
          <Icon size={18} />
        </span>
      )}
      <div className="toast__content">
        {title && <div className="toast__title">{title}</div>}
        <div className="toast__message">{message}</div>
        {action && (
          <button 
            className="toast__action" 
            onClick={() => {
              action.onClick?.();
              handleRemove();
            }}
          >
            {action.label}
          </button>
        )}
      </div>
      <IconButton
        variant="ghost"
        size="sm"
        label="Dismiss"
        onClick={handleRemove}
        className="toast__close"
      >
        <X size={16} />
      </IconButton>
    </div>
  );
}

export default ToastProvider;
