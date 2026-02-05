import { useState, useEffect, useRef, useCallback } from 'react';
import { PanelLeftClose, PanelLeftOpen, PanelRightClose, PanelRightOpen } from 'lucide-react';
import IconButton from '../../ui/IconButton';
import Tooltip from '../../ui/Tooltip';
import { LayoutContext } from './LayoutContext';
import './WorkspaceLayout.css';

const STORAGE_KEY = 'workspace-layout';
const MOBILE_BREAKPOINT = 768;

/**
 * Load persisted state from localStorage
 */
function loadPersistedState() {
  try {
    const saved = localStorage.getItem(STORAGE_KEY);
    if (saved) {
      return JSON.parse(saved);
    }
  } catch (e) {
    console.warn('Failed to load workspace layout state:', e);
  }
  return null;
}

/**
 * Save state to localStorage
 */
function persistState(state) {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(state));
  } catch (e) {
    console.warn('Failed to save workspace layout state:', e);
  }
}

/**
 * Main 3-panel workspace layout
 */
function WorkspaceLayout({ 
  children,
  leftPanel,
  rightPanel,
  header,
  defaultLeftCollapsed = false,
  defaultRightCollapsed = false,
  defaultLeftWidth = 280,
  defaultRightWidth = 320,
  minLeftWidth = 200,
  maxLeftWidth = 400,
  minRightWidth = 280,
  maxRightWidth = 480,
}) {
  const savedState = loadPersistedState();
  
  const [leftCollapsed, setLeftCollapsed] = useState(
    savedState?.leftCollapsed ?? defaultLeftCollapsed
  );
  const [rightCollapsed, setRightCollapsed] = useState(
    savedState?.rightCollapsed ?? defaultRightCollapsed
  );
  const [leftWidth, setLeftWidth] = useState(
    savedState?.leftWidth ?? defaultLeftWidth
  );
  const [rightWidth, setRightWidth] = useState(
    savedState?.rightWidth ?? defaultRightWidth
  );
  const [isMobile, setIsMobile] = useState(
    typeof window !== 'undefined' && window.innerWidth <= MOBILE_BREAKPOINT
  );
  const [mobileDrawer, setMobileDrawer] = useState(null); // 'left' | 'right' | null

  const layoutRef = useRef(null);
  const isResizing = useRef(null);

  // Handle window resize
  useEffect(() => {
    const handleResize = () => {
      const mobile = window.innerWidth <= MOBILE_BREAKPOINT;
      setIsMobile(mobile);
      if (mobile) {
        setMobileDrawer(null);
      }
    };

    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  // Persist state changes
  useEffect(() => {
    persistState({ leftCollapsed, rightCollapsed, leftWidth, rightWidth });
  }, [leftCollapsed, rightCollapsed, leftWidth, rightWidth]);

  // Toggle functions
  const toggleLeftPanel = useCallback(() => {
    if (isMobile) {
      setMobileDrawer(prev => prev === 'left' ? null : 'left');
    } else {
      setLeftCollapsed(prev => !prev);
    }
  }, [isMobile]);

  const toggleRightPanel = useCallback(() => {
    if (isMobile) {
      setMobileDrawer(prev => prev === 'right' ? null : 'right');
    } else {
      setRightCollapsed(prev => !prev);
    }
  }, [isMobile]);

  const closeMobileDrawer = useCallback(() => {
    setMobileDrawer(null);
  }, []);

  // Resize handling
  const handleResizeStart = useCallback((side) => (e) => {
    e.preventDefault();
    isResizing.current = side;
    document.body.style.cursor = 'col-resize';
    document.body.style.userSelect = 'none';
  }, []);

  const handleResizeMove = useCallback((e) => {
    if (!isResizing.current || !layoutRef.current) return;

    const layoutRect = layoutRef.current.getBoundingClientRect();
    
    if (isResizing.current === 'left') {
      const newWidth = e.clientX - layoutRect.left;
      setLeftWidth(Math.max(minLeftWidth, Math.min(maxLeftWidth, newWidth)));
    } else if (isResizing.current === 'right') {
      const newWidth = layoutRect.right - e.clientX;
      setRightWidth(Math.max(minRightWidth, Math.min(maxRightWidth, newWidth)));
    }
  }, [minLeftWidth, maxLeftWidth, minRightWidth, maxRightWidth]);

  const handleResizeEnd = useCallback(() => {
    isResizing.current = null;
    document.body.style.cursor = '';
    document.body.style.userSelect = '';
  }, []);

  useEffect(() => {
    document.addEventListener('mousemove', handleResizeMove);
    document.addEventListener('mouseup', handleResizeEnd);
    return () => {
      document.removeEventListener('mousemove', handleResizeMove);
      document.removeEventListener('mouseup', handleResizeEnd);
    };
  }, [handleResizeMove, handleResizeEnd]);

  // Keyboard shortcuts
  useEffect(() => {
    const handleKeyDown = (e) => {
      // Cmd/Ctrl + B: Toggle left panel
      if ((e.metaKey || e.ctrlKey) && e.key === 'b') {
        e.preventDefault();
        toggleLeftPanel();
      }
      // Cmd/Ctrl + Shift + B: Toggle right panel
      if ((e.metaKey || e.ctrlKey) && e.shiftKey && e.key === 'B') {
        e.preventDefault();
        toggleRightPanel();
      }
      // Escape: Close mobile drawer
      if (e.key === 'Escape' && mobileDrawer) {
        closeMobileDrawer();
      }
    };

    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, [toggleLeftPanel, toggleRightPanel, mobileDrawer, closeMobileDrawer]);

  const contextValue = {
    leftCollapsed,
    rightCollapsed,
    leftWidth,
    rightWidth,
    isMobile,
    mobileDrawer,
    toggleLeftPanel,
    toggleRightPanel,
    closeMobileDrawer,
    setLeftWidth,
    setRightWidth,
  };

  return (
    <LayoutContext.Provider value={contextValue}>
      <div className="workspace-layout" ref={layoutRef}>
        {header}
        
        <div className="workspace-layout__body">
          {/* Left Panel */}
          {!isMobile && (
            <>
              <aside 
                className={`workspace-panel workspace-panel--left ${leftCollapsed ? 'workspace-panel--collapsed' : ''}`}
                style={{ width: leftCollapsed ? 0 : leftWidth }}
                aria-label="Sources panel"
              >
                <div className="workspace-panel__content">
                  {leftPanel}
                </div>
              </aside>
              
              {/* Left Resize Handle */}
              {!leftCollapsed && (
                <div 
                  className="resize-handle resize-handle--left"
                  onMouseDown={handleResizeStart('left')}
                  aria-hidden="true"
                />
              )}
            </>
          )}

          {/* Center Panel */}
          <main className="workspace-panel workspace-panel--center">
            {/* Panel toggle buttons for desktop */}
            {!isMobile && (
              <div className="workspace-panel__toggle workspace-panel__toggle--left">
                <Tooltip content={leftCollapsed ? 'Open sources (⌘B)' : 'Close sources (⌘B)'} position="right">
                  <IconButton
                    variant="ghost"
                    size="sm"
                    label={leftCollapsed ? 'Open sources panel' : 'Close sources panel'}
                    onClick={toggleLeftPanel}
                  >
                    {leftCollapsed ? <PanelLeftOpen size={18} /> : <PanelLeftClose size={18} />}
                  </IconButton>
                </Tooltip>
              </div>
            )}
            
            <div className="workspace-panel__content">
              {children}
            </div>
            
            {!isMobile && (
              <div className="workspace-panel__toggle workspace-panel__toggle--right">
                <Tooltip content={rightCollapsed ? 'Open study tools (⌘⇧B)' : 'Close study tools (⌘⇧B)'} position="left">
                  <IconButton
                    variant="ghost"
                    size="sm"
                    label={rightCollapsed ? 'Open study tools panel' : 'Close study tools panel'}
                    onClick={toggleRightPanel}
                  >
                    {rightCollapsed ? <PanelRightOpen size={18} /> : <PanelRightClose size={18} />}
                  </IconButton>
                </Tooltip>
              </div>
            )}
          </main>

          {/* Right Panel */}
          {!isMobile && (
            <>
              {/* Right Resize Handle */}
              {!rightCollapsed && (
                <div 
                  className="resize-handle resize-handle--right"
                  onMouseDown={handleResizeStart('right')}
                  aria-hidden="true"
                />
              )}
              
              <aside 
                className={`workspace-panel workspace-panel--right ${rightCollapsed ? 'workspace-panel--collapsed' : ''}`}
                style={{ width: rightCollapsed ? 0 : rightWidth }}
                aria-label="Study tools panel"
              >
                <div className="workspace-panel__content">
                  {rightPanel}
                </div>
              </aside>
            </>
          )}
        </div>

        {/* Mobile Drawer Backdrop */}
        {isMobile && mobileDrawer && (
          <div 
            className="mobile-drawer-backdrop"
            onClick={closeMobileDrawer}
            aria-hidden="true"
          />
        )}

        {/* Mobile Left Drawer */}
        {isMobile && (
          <aside 
            className={`mobile-drawer mobile-drawer--left ${mobileDrawer === 'left' ? 'mobile-drawer--open' : ''}`}
            aria-label="Sources panel"
            aria-hidden={mobileDrawer !== 'left'}
          >
            <div className="mobile-drawer__content">
              {leftPanel}
            </div>
          </aside>
        )}

        {/* Mobile Right Drawer */}
        {isMobile && (
          <aside 
            className={`mobile-drawer mobile-drawer--right ${mobileDrawer === 'right' ? 'mobile-drawer--open' : ''}`}
            aria-label="Study tools panel"
            aria-hidden={mobileDrawer !== 'right'}
          >
            <div className="mobile-drawer__content">
              {rightPanel}
            </div>
          </aside>
        )}
      </div>
    </LayoutContext.Provider>
  );
}

export default WorkspaceLayout;
