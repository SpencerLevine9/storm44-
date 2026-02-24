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
  minRightWidth = 420, // Updated per AR-02
  maxRightWidth = 800, // Increased max width
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

  // AR-01: Fullscreen State
  const [studyToolsFullscreen, setStudyToolsFullscreen] = useState(false);
  const [preFullscreenSnapshot, setPreFullscreenSnapshot] = useState(null);

  // AR-02: 2/3 Preset State
  const [studyPresetActive, setStudyPresetActive] = useState(false);
  const [prePresetSnapshot, setPrePresetSnapshot] = useState(null);

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

  // Persist state changes (only normal layout)
  useEffect(() => {
    if (!studyToolsFullscreen && !studyPresetActive) {
      persistState({ leftCollapsed, rightCollapsed, leftWidth, rightWidth });
    }
  }, [leftCollapsed, rightCollapsed, leftWidth, rightWidth, studyToolsFullscreen, studyPresetActive]);

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

  // AR-01: Fullscreen Logic
  const enterFullscreen = useCallback(() => {
    setPreFullscreenSnapshot({
      leftCollapsed,
      rightCollapsed,
      leftWidth,
      rightWidth
    });
    setStudyToolsFullscreen(true);
    // In Fullscreen, we basically strictly show Right Panel.
    // We don't necessarily need to mutate collapsed state if we just don't render them.
    // But setting rightCollapsed to false is important to ensure it's visible.
    setRightCollapsed(false);
  }, [leftCollapsed, rightCollapsed, leftWidth, rightWidth]);

  const exitFullscreen = useCallback(() => {
    setStudyToolsFullscreen(false);
    if (preFullscreenSnapshot) {
      setLeftCollapsed(preFullscreenSnapshot.leftCollapsed);
      setRightCollapsed(preFullscreenSnapshot.rightCollapsed);
      setLeftWidth(preFullscreenSnapshot.leftWidth);
      setRightWidth(preFullscreenSnapshot.rightWidth);
      setPreFullscreenSnapshot(null);
    }
  }, [preFullscreenSnapshot]);

  // AR-02: Preset Logic — collapse sources, chat 1/3, study tools 2/3
  const setRightPanelWidthPreset = useCallback(() => {
    if (typeof window === 'undefined') return;

    // Save current state so we can revert later
    setPrePresetSnapshot({
      leftCollapsed,
      rightCollapsed,
      leftWidth,
      rightWidth,
    });

    const totalWidth = window.innerWidth;
    const targetRightWidth = Math.floor(totalWidth * (2 / 3));

    setLeftCollapsed(true);       // Collapse sources panel
    setRightCollapsed(false);     // Ensure study tools open
    setRightWidth(Math.max(minRightWidth, targetRightWidth));
    setStudyPresetActive(true);
  }, [leftCollapsed, rightCollapsed, leftWidth, rightWidth, minRightWidth]);

  // Revert preset — restore panels to defaults
  const revertPreset = useCallback(() => {
    if (prePresetSnapshot) {
      setLeftCollapsed(prePresetSnapshot.leftCollapsed);
      setRightCollapsed(prePresetSnapshot.rightCollapsed);
      setLeftWidth(prePresetSnapshot.leftWidth);
      setRightWidth(prePresetSnapshot.rightWidth);
      setPrePresetSnapshot(null);
    } else {
      // Fallback to prop defaults
      setLeftCollapsed(defaultLeftCollapsed);
      setRightCollapsed(defaultRightCollapsed);
      setLeftWidth(defaultLeftWidth);
      setRightWidth(defaultRightWidth);
    }
    setStudyPresetActive(false);
  }, [prePresetSnapshot, defaultLeftCollapsed, defaultRightCollapsed, defaultLeftWidth, defaultRightWidth]);


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

      // AR-02: Min Chat Width = 320px
      const currentLeftWidth = (leftCollapsed || isMobile) ? 0 : leftWidth;
      const maxAllowedWidth = layoutRect.width - currentLeftWidth - 320;

      const constrainedWidth = Math.min(newWidth, maxAllowedWidth);

      // Also respect maxRightWidth if provided, though 2/3 preset might exceed old defaults
      // We use the new maxRightWidth prop or a robust large number
      setRightWidth(Math.max(minRightWidth, Math.min(maxRightWidth * 1.5, constrainedWidth)));
    }
  }, [minLeftWidth, maxLeftWidth, minRightWidth, maxRightWidth, leftCollapsed, isMobile, leftWidth]);

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
      // Escape: Close mobile drawer OR Exit Fullscreen
      if (e.key === 'Escape') {
        if (studyToolsFullscreen) {
          exitFullscreen();
        } else if (mobileDrawer) {
          closeMobileDrawer();
        }
      }
    };

    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, [toggleLeftPanel, toggleRightPanel, mobileDrawer, closeMobileDrawer, studyToolsFullscreen, exitFullscreen]);

  const contextValue = {
    leftCollapsed,
    rightCollapsed,
    leftWidth,
    rightWidth,
    isMobile,
    mobileDrawer,
    studyToolsFullscreen,
    toggleLeftPanel,
    toggleRightPanel,
    closeMobileDrawer,
    setLeftWidth,
    setRightWidth,
    enterFullscreen,
    exitFullscreen,
    setRightPanelWidthPreset,
    studyPresetActive,
    revertPreset,
  };

  return (
    <LayoutContext.Provider value={contextValue}>
      <div className="workspace-layout" ref={layoutRef}>
        {!studyToolsFullscreen && header}

        <div className="workspace-layout__body">
          {/* Left Panel */}
          {!isMobile && !studyToolsFullscreen && (
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
          {!studyToolsFullscreen ? (
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
          ) : null}

          {/* Right Panel */}
          {!isMobile && (
            <>
              {/* Right Resize Handle - Hide in Fullscreen */}
              {!rightCollapsed && !studyToolsFullscreen && (
                <div
                  className="resize-handle resize-handle--right"
                  onMouseDown={handleResizeStart('right')}
                  aria-hidden="true"
                />
              )}

              <aside
                className={`workspace-panel workspace-panel--right ${rightCollapsed ? 'workspace-panel--collapsed' : ''}`}
                style={{
                  width: studyToolsFullscreen
                    ? '100%'
                    : (rightCollapsed ? 0 : rightWidth),
                  flex: studyToolsFullscreen ? 1 : undefined
                }}
                aria-label="Study tools panel"
              >
                <div className="workspace-panel__content">
                  {rightPanel}
                </div>
              </aside>
            </>
          )}
        </div>

        {/* ... Mobile drawers ... (Keep existing) */}
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

        {/* Mobile Right Drawer - Update for fullscreen-like behavior on mobile if needed, or keep standard */}
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
