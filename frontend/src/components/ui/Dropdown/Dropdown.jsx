import { useState, useRef, useEffect, createContext, useContext, useCallback, useLayoutEffect } from 'react';
import { createPortal } from 'react-dom';
import { Check } from 'lucide-react';
import './Dropdown.css';

const DropdownContext = createContext(null);

/**
 * Dropdown menu container
 */
export function Dropdown({ children, className = '' }) {
  const [isOpen, setIsOpen] = useState(false);
  const [position, setPosition] = useState({ top: 0, left: 0 });
  const triggerRef = useRef(null);
  const menuRef = useRef(null);

  const open = useCallback(() => setIsOpen(true), []);
  const close = useCallback(() => setIsOpen(false), []);
  const toggle = useCallback(() => setIsOpen(prev => !prev), []);

  // Position the menu when opened - use useLayoutEffect to avoid flash
  useLayoutEffect(() => {
    if (!isOpen) return;
    
    const updatePosition = () => {
      const trigger = triggerRef.current;
      const menu = menuRef.current;
      if (!trigger || !menu) return;

      const triggerRect = trigger.getBoundingClientRect();
      const menuRect = menu.getBoundingClientRect();
      const gap = 4;
      
      let top = triggerRect.bottom + gap;
      let left = triggerRect.left;

      // Adjust if menu would go off-screen
      if (top + menuRect.height > window.innerHeight - 8) {
        top = triggerRect.top - menuRect.height - gap;
      }
      if (left + menuRect.width > window.innerWidth - 8) {
        left = window.innerWidth - menuRect.width - 8;
      }
      if (left < 8) {
        left = 8;
      }

      setPosition({ top, left });
    };

    // Use requestAnimationFrame to batch with browser paint
    requestAnimationFrame(updatePosition);
  }, [isOpen]);

  // Close on outside click
  useEffect(() => {
    if (!isOpen) return;

    const handleClickOutside = (e) => {
      const menu = menuRef.current;
      const trigger = triggerRef.current;
      if (
        menu && 
        !menu.contains(e.target) &&
        trigger &&
        !trigger.contains(e.target)
      ) {
        close();
      }
    };

    const handleEscape = (e) => {
      if (e.key === 'Escape') {
        close();
        triggerRef.current?.focus();
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    document.addEventListener('keydown', handleEscape);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
      document.removeEventListener('keydown', handleEscape);
    };
  }, [isOpen, close]);

  const contextValue = {
    isOpen,
    open,
    close,
    toggle,
    triggerRef,
    menuRef,
    position,
  };

  return (
    <DropdownContext.Provider value={contextValue}>
      <div className={`dropdown ${className}`}>
        {children}
      </div>
    </DropdownContext.Provider>
  );
}

/**
 * Dropdown trigger button
 */
export function DropdownTrigger({ children, asChild = false }) {
  const context = useContext(DropdownContext);
  if (!context) throw new Error('DropdownTrigger must be used within Dropdown');

  const { toggle, open, isOpen, triggerRef } = context;

  const handleClick = (e) => {
    e.stopPropagation();
    toggle();
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' || e.key === ' ' || e.key === 'ArrowDown') {
      e.preventDefault();
      open();
    }
  };

  if (asChild && children) {
    return (
      <span
        ref={triggerRef}
        onClick={handleClick}
        onKeyDown={handleKeyDown}
      >
        {children}
      </span>
    );
  }

  return (
    <button
      ref={triggerRef}
      type="button"
      className="dropdown-trigger"
      onClick={handleClick}
      onKeyDown={handleKeyDown}
      aria-haspopup="menu"
      aria-expanded={isOpen}
    >
      {children}
    </button>
  );
}

/**
 * Dropdown menu content
 */
export function DropdownMenu({ children, align = 'start', className = '' }) {
  const context = useContext(DropdownContext);
  if (!context) throw new Error('DropdownMenu must be used within Dropdown');

  const { isOpen, menuRef, position } = context;

  if (!isOpen) return null;

  const menu = (
    <div
      ref={menuRef}
      className={`dropdown-menu dropdown-menu--${align} ${className}`}
      style={{ top: position.top, left: position.left }}
      role="menu"
      tabIndex={-1}
    >
      {children}
    </div>
  );

  return createPortal(menu, document.body);
}

/**
 * Dropdown menu item
 */
export function DropdownItem({ 
  children, 
  onClick, 
  disabled = false,
  destructive = false,
  icon,
  shortcut,
  className = ''
}) {
  const context = useContext(DropdownContext);
  if (!context) throw new Error('DropdownItem must be used within Dropdown');

  const { close } = context;

  const handleClick = (e) => {
    if (disabled) return;
    onClick?.(e);
    close();
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' || e.key === ' ') {
      e.preventDefault();
      handleClick(e);
    }
  };

  const classes = [
    'dropdown-item',
    disabled && 'dropdown-item--disabled',
    destructive && 'dropdown-item--destructive',
    className
  ].filter(Boolean).join(' ');

  return (
    <button
      type="button"
      className={classes}
      role="menuitem"
      disabled={disabled}
      onClick={handleClick}
      onKeyDown={handleKeyDown}
    >
      {icon && <span className="dropdown-item__icon">{icon}</span>}
      <span className="dropdown-item__label">{children}</span>
      {shortcut && <span className="dropdown-item__shortcut">{shortcut}</span>}
    </button>
  );
}

/**
 * Dropdown checkbox item
 */
export function DropdownCheckboxItem({ 
  children, 
  checked = false,
  onCheckedChange,
  disabled = false,
  className = ''
}) {
  const context = useContext(DropdownContext);
  if (!context) throw new Error('DropdownCheckboxItem must be used within Dropdown');

  const handleClick = () => {
    if (disabled) return;
    onCheckedChange?.(!checked);
  };

  const classes = [
    'dropdown-item',
    'dropdown-item--checkbox',
    disabled && 'dropdown-item--disabled',
    className
  ].filter(Boolean).join(' ');

  return (
    <button
      type="button"
      className={classes}
      role="menuitemcheckbox"
      aria-checked={checked}
      disabled={disabled}
      onClick={handleClick}
    >
      <span className="dropdown-item__check">
        {checked && <Check size={14} />}
      </span>
      <span className="dropdown-item__label">{children}</span>
    </button>
  );
}

/**
 * Dropdown separator
 */
export function DropdownSeparator() {
  return <div className="dropdown-separator" role="separator" />;
}

/**
 * Dropdown label/group header
 */
export function DropdownLabel({ children, className = '' }) {
  return (
    <div className={`dropdown-label ${className}`}>
      {children}
    </div>
  );
}

export default Dropdown;
