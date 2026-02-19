import { useState, useCallback } from 'react';
import { WorkspaceLayout, Header } from '../../components/layout';
import SourcesPanel from '../../features/sources/SourcesPanel';
import ChatPanel from '../../features/chat/ChatPanel';
import StudyToolsPanel from '../../features/study-tools/StudyToolsPanel';
import './WorkspacePage.css';

/**
 * Main workspace page with 3-panel layout
 */
function WorkspacePage() {
  const [conversationId, setConversationId] = useState(() => Date.now().toString());

  const handleNewChat = useCallback(() => {
    setConversationId(Date.now().toString());
  }, []);

  return (
    <WorkspaceLayout
      header={
        <Header
          onNewChat={handleNewChat}
        />
      }
      leftPanel={<SourcesPanel />}
      rightPanel={<StudyToolsPanel />}
    >
      <ChatPanel key={conversationId} />
    </WorkspaceLayout>
  );
}

export default WorkspacePage;
