export interface Message {
  id: string;
  content: string;
  role: 'user' | 'assistant';
  timestamp: Date;
  thinking?: string;
}

export interface ChatSession {
  id: string;
  title: string;
  messages: Message[];
  createdAt: Date;
  updatedAt: Date;
  isPinned: boolean;
  model?: string;
}

const STORAGE_KEY = 'ollama_chat_sessions';

export function getAllSessions(): ChatSession[] {
  try {
    const stored = localStorage.getItem(STORAGE_KEY);
    if (!stored) return [];

    const sessions = JSON.parse(stored);
    return sessions.map((session: any) => ({
      ...session,
      createdAt: new Date(session.createdAt),
      updatedAt: new Date(session.updatedAt),
      messages: session.messages.map((msg: any) => ({
        ...msg,
        timestamp: new Date(msg.timestamp),
      })),
    }));
  } catch (error) {
    console.error('Error loading chat sessions:', error);
    return [];
  }
}

export function getSession(sessionId: string): ChatSession | null {
  const sessions = getAllSessions();
  return sessions.find(s => s.id === sessionId) || null;
}

export function saveSession(session: ChatSession): void {
  try {
    const sessions = getAllSessions();
    const existingIndex = sessions.findIndex(s => s.id === session.id);

    if (existingIndex >= 0) {
      sessions[existingIndex] = session;
    } else {
      sessions.push(session);
    }

    localStorage.setItem(STORAGE_KEY, JSON.stringify(sessions));
  } catch (error) {
    console.error('Error saving chat session:', error);
  }
}

export function deleteSession(sessionId: string): void {
  try {
    const sessions = getAllSessions();
    const filtered = sessions.filter(s => s.id !== sessionId);
    localStorage.setItem(STORAGE_KEY, JSON.stringify(filtered));
  } catch (error) {
    console.error('Error deleting chat session:', error);
  }
}

export function updateSessionTitle(sessionId: string, newTitle: string): void {
  try {
    const sessions = getAllSessions();
    const session = sessions.find(s => s.id === sessionId);

    if (session) {
      session.title = newTitle;
      session.updatedAt = new Date();
      localStorage.setItem(STORAGE_KEY, JSON.stringify(sessions));
    }
  } catch (error) {
    console.error('Error updating session title:', error);
  }
}

export function togglePinSession(sessionId: string): void {
  try {
    const sessions = getAllSessions();
    const session = sessions.find(s => s.id === sessionId);

    if (session) {
      session.isPinned = !session.isPinned;
      session.updatedAt = new Date();
      localStorage.setItem(STORAGE_KEY, JSON.stringify(sessions));
    }
  } catch (error) {
    console.error('Error toggling pin status:', error);
  }
}

export function clearAllSessions(): void {
  try {
    localStorage.removeItem(STORAGE_KEY);
  } catch (error) {
    console.error('Error clearing all sessions:', error);
  }
}

export function createNewSession(model?: string): ChatSession {
  // Generate a unique ID using timestamp + random string to avoid collisions
  const uniqueId = `${Date.now()}-${Math.random().toString(36).substring(2, 9)}`;

  const newSession: ChatSession = {
    id: uniqueId,
    title: 'New Chat',
    messages: [],
    createdAt: new Date(),
    updatedAt: new Date(),
    isPinned: false,
    model,
  };

  // Save the new session immediately to localStorage
  saveSession(newSession);

  return newSession;
}

export function generateSessionTitle(messages: Message[]): string {
  if (messages.length === 0) return 'New Chat';

  const firstUserMessage = messages.find(m => m.role === 'user');
  if (!firstUserMessage) return 'New Chat';

  const title = firstUserMessage.content.slice(0, 50);
  return title.length < firstUserMessage.content.length ? `${title}...` : title;
}
