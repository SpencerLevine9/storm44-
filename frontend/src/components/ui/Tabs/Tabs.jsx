import { createContext, useContext, useId, useState } from 'react';
import './Tabs.css';

const TabsContext = createContext(null);

/**
 * Tabs container component
 */
export function Tabs({ 
  children, 
  defaultValue, 
  value: controlledValue, 
  onValueChange,
  className = '' 
}) {
  const [uncontrolledValue, setUncontrolledValue] = useState(defaultValue);
  const isControlled = controlledValue !== undefined;
  const value = isControlled ? controlledValue : uncontrolledValue;

  const handleValueChange = (newValue) => {
    if (!isControlled) {
      setUncontrolledValue(newValue);
    }
    onValueChange?.(newValue);
  };

  return (
    <TabsContext.Provider value={{ value, onValueChange: handleValueChange }}>
      <div className={`tabs ${className}`}>
        {children}
      </div>
    </TabsContext.Provider>
  );
}

/**
 * Tab list container (the row of tab buttons)
 */
export function TabList({ children, className = '', 'aria-label': ariaLabel }) {
  return (
    <div 
      className={`tabs-list ${className}`} 
      role="tablist"
      aria-label={ariaLabel}
    >
      {children}
    </div>
  );
}

/**
 * Individual tab button
 */
export function Tab({ 
  children, 
  value, 
  disabled = false, 
  className = '' 
}) {
  const context = useContext(TabsContext);
  const id = useId();
  const tabId = `tab-${id}`;
  const panelId = `panel-${id}`;
  
  if (!context) {
    throw new Error('Tab must be used within a Tabs component');
  }

  const isSelected = context.value === value;

  const handleClick = () => {
    if (!disabled) {
      context.onValueChange(value);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' || e.key === ' ') {
      e.preventDefault();
      handleClick();
    }
  };

  const classes = [
    'tab',
    isSelected && 'tab--selected',
    disabled && 'tab--disabled',
    className
  ].filter(Boolean).join(' ');

  return (
    <button
      id={tabId}
      type="button"
      role="tab"
      className={classes}
      aria-selected={isSelected}
      aria-controls={panelId}
      aria-disabled={disabled}
      tabIndex={isSelected ? 0 : -1}
      onClick={handleClick}
      onKeyDown={handleKeyDown}
      disabled={disabled}
    >
      {children}
    </button>
  );
}

/**
 * Tab panel content
 */
export function TabPanel({ 
  children, 
  value, 
  className = '',
  forceMount = false
}) {
  const context = useContext(TabsContext);
  const id = useId();
  const tabId = `tab-${id}`;
  const panelId = `panel-${id}`;
  
  if (!context) {
    throw new Error('TabPanel must be used within a Tabs component');
  }

  const isSelected = context.value === value;

  if (!isSelected && !forceMount) {
    return null;
  }

  const classes = [
    'tab-panel',
    !isSelected && 'tab-panel--hidden',
    className
  ].filter(Boolean).join(' ');

  return (
    <div
      id={panelId}
      role="tabpanel"
      className={classes}
      aria-labelledby={tabId}
      tabIndex={0}
      hidden={!isSelected}
    >
      {children}
    </div>
  );
}

export default Tabs;
