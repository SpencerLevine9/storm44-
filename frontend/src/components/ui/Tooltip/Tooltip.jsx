import { useState, useRef, useEffect, useCallback } from 'react';
import { createPortal } from 'react-dom';
import './Tooltip.css';

/**
 * Tooltip component with iOS-like styling
 */
function Tooltip({
  children,
  content,
  position = 'top',
  delay = 200,
  disabled = false,
  className = ''
}) {
  const [isVisible, setIsVisible] = useState(false);
  const [coords, setCoords] = useState({ top: 0, left: 0 });
  const triggerRef = useRef(null);
  const tooltipRef = useRef(null);
  const timeoutRef = useRef(null);

  const showTooltip = useCallback(() => {
    if (disabled) return;
    
    timeoutRef.current = setTimeout(() => {
      setIsVisible(true);
    }, delay);
  }, [disabled, delay]);

  const hideTooltip = useCallback(() => {
    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current);
    }
    setIsVisible(false);
  }, []);

  useEffect(() => {
    if (isVisible && triggerRef.current && tooltipRef.current) {
      const triggerRect = triggerRef.current.getBoundingClientRect();
      const tooltipRect = tooltipRef.current.getBoundingClientRect();
      const scrollX = window.scrollX;
      const scrollY = window.scrollY;
      const gap = 8;

      let top, left;

      switch (position) {
        case 'top':
          top = triggerRect.top + scrollY - tooltipRect.height - gap;
          left = triggerRect.left + scrollX + (triggerRect.width - tooltipRect.width) / 2;
          break;
        case 'bottom':
          top = triggerRect.bottom + scrollY + gap;
          left = triggerRect.left + scrollX + (triggerRect.width - tooltipRect.width) / 2;
          break;
        case 'left':
          top = triggerRect.top + scrollY + (triggerRect.height - tooltipRect.height) / 2;
          left = triggerRect.left + scrollX - tooltipRect.width - gap;
          break;
        case 'right':
          top = triggerRect.top + scrollY + (triggerRect.height - tooltipRect.height) / 2;
          left = triggerRect.right + scrollX + gap;
          break;
        default:
          top = triggerRect.top + scrollY - tooltipRect.height - gap;
          left = triggerRect.left + scrollX + (triggerRect.width - tooltipRect.width) / 2;
      }

      // Keep tooltip within viewport
      const padding = 8;
      left = Math.max(padding, Math.min(left, window.innerWidth - tooltipRect.width - padding));
      top = Math.max(padding, Math.min(top, window.innerHeight - tooltipRect.height - padding));

      setCoords({ top, left });
    }
  }, [isVisible, position]);

  useEffect(() => {
    return () => {
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current);
      }
    };
  }, []);

  if (!content) return children;

  return (
    <>
      <span
        ref={triggerRef}
        onMouseEnter={showTooltip}
        onMouseLeave={hideTooltip}
        onFocus={showTooltip}
        onBlur={hideTooltip}
        style={{ display: 'inline-flex' }}
      >
        {children}
      </span>
      {isVisible && createPortal(
        <div
          ref={tooltipRef}
          className={`tooltip tooltip--${position} ${className}`}
          style={{ top: coords.top, left: coords.left }}
          role="tooltip"
        >
          {content}
        </div>,
        document.body
      )}
    </>
  );
}

export default Tooltip;
