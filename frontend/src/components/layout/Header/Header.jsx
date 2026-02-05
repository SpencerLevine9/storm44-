import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  Menu, 
  Plus, 
  Settings, 
  BookOpen,
  PanelLeft,
  PanelRight,
  Moon,
  Sun,
  HelpCircle,
  LogOut
} from 'lucide-react';
import { useLayout } from '../WorkspaceLayout';
import IconButton from '../../ui/IconButton';
import Button from '../../ui/Button';
import Tooltip from '../../ui/Tooltip';
import {
  Dropdown,
  DropdownTrigger,
  DropdownMenu,
  DropdownItem,
  DropdownSeparator,
  DropdownLabel,
} from '../../ui/Dropdown';
import './Header.css';

/**
 * App header with workspace title and navigation
 */
function Header({ 
  workspaceName = 'Untitled Workspace',
  onNewChat,
  onRename,
}) {
  const navigate = useNavigate();
  const layout = useLayout();
  const [isDarkMode, setIsDarkMode] = useState(false);

  const handleNewChat = () => {
    onNewChat?.();
  };

  const handleToggleTheme = () => {
    setIsDarkMode(!isDarkMode);
    document.documentElement.setAttribute('data-theme', isDarkMode ? 'light' : 'dark');
  };

  const handleOpenSettings = () => {
    navigate('/settings');
  };

  return (
    <header className="header">
      <div className="header__left">
        {/* Mobile menu button */}
        {layout.isMobile && (
          <IconButton
            variant="ghost"
            size="md"
            label="Open sources"
            onClick={layout.toggleLeftPanel}
          >
            <PanelLeft size={20} />
          </IconButton>
        )}

        {/* Logo/Brand */}
        <div className="header__brand">
          <BookOpen size={22} className="header__logo" />
          <span className="header__app-name">Storm44</span>
        </div>

        {/* Workspace name */}
        <div className="header__workspace">
          <span className="header__separator">/</span>
          <button 
            className="header__workspace-name"
            onClick={onRename}
            title="Click to rename"
          >
            {workspaceName}
          </button>
        </div>
      </div>

      <div className="header__center">
        {/* New Chat button */}
        <Button
          variant="primary"
          size="sm"
          leftIcon={<Plus size={16} />}
          onClick={handleNewChat}
        >
          New Chat
        </Button>
      </div>

      <div className="header__right">
        {/* Mobile study tools button */}
        {layout.isMobile && (
          <IconButton
            variant="ghost"
            size="md"
            label="Open study tools"
            onClick={layout.toggleRightPanel}
          >
            <PanelRight size={20} />
          </IconButton>
        )}

        {/* Theme toggle */}
        <Tooltip content={isDarkMode ? 'Light mode' : 'Dark mode'}>
          <IconButton
            variant="ghost"
            size="md"
            label={isDarkMode ? 'Switch to light mode' : 'Switch to dark mode'}
            onClick={handleToggleTheme}
          >
            {isDarkMode ? <Sun size={20} /> : <Moon size={20} />}
          </IconButton>
        </Tooltip>

        {/* Settings menu */}
        <Dropdown>
          <DropdownTrigger>
            <IconButton
              variant="ghost"
              size="md"
              label="Settings menu"
            >
              <Settings size={20} />
            </IconButton>
          </DropdownTrigger>
          <DropdownMenu align="end">
            <DropdownLabel>Settings</DropdownLabel>
            <DropdownItem 
              icon={<Settings size={16} />}
              onClick={handleOpenSettings}
            >
              Preferences
            </DropdownItem>
            <DropdownItem icon={<HelpCircle size={16} />}>
              Help & Support
            </DropdownItem>
            <DropdownSeparator />
            <DropdownItem 
              icon={isDarkMode ? <Sun size={16} /> : <Moon size={16} />}
              onClick={handleToggleTheme}
            >
              {isDarkMode ? 'Light Mode' : 'Dark Mode'}
            </DropdownItem>
            <DropdownSeparator />
            <DropdownItem 
              icon={<LogOut size={16} />}
              destructive
            >
              Sign Out
            </DropdownItem>
          </DropdownMenu>
        </Dropdown>
      </div>
    </header>
  );
}

export default Header;
