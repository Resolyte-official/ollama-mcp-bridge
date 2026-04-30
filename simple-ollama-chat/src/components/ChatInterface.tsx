import { useState, useEffect } from "react";
import { ChatMessage } from "./ChatMessage";
import { ChatInput } from "./ChatInput";
import { SettingsPanel } from "./SettingsPanel";
import { ChatHistoryNav } from "./ChatHistoryNav";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Trash2, MessageSquare, RefreshCw } from "lucide-react";
import { cn } from "@/lib/utils";
import { useChatState } from "@/hooks/useChatState";
import { useSettings } from "@/hooks/useSettings";
import { useToast } from "@/hooks/use-toast";
import type { ChatSession } from "@/lib/chatHistory";
import {
  getAllSessions,
  createNewSession,
  deleteSession,
  updateSessionTitle,
  togglePinSession,
  clearAllSessions,
} from "@/lib/chatHistory";

interface OllamaModel {
  name: string;
  model: string;
  size: number;
  digest: string;
}

const DEFAULT_OLLAMA_URL = "http://localhost:11434";

export function ChatInterface() {
  const [selectedModel, setSelectedModel] = useState("");
  const [ollamaUrl, setOllamaUrl] = useState(DEFAULT_OLLAMA_URL);
  const [models, setModels] = useState<OllamaModel[]>([]);
  const [isLoadingModels, setIsLoadingModels] = useState(false);
  const [sessions, setSessions] = useState<ChatSession[]>([]);
  const [currentSession, setCurrentSession] = useState<ChatSession | null>(
    null
  );
  const { toast } = useToast();

  // Load saved model and URL from localStorage on mount
  useEffect(() => {
    const savedModel = localStorage.getItem('selectedModel');
    if (savedModel) {
      setSelectedModel(savedModel);
    }

    const savedUrl = localStorage.getItem('ollamaUrl');
    if (savedUrl) {
      setOllamaUrl(savedUrl);
    }
  }, []);

  const { thinkingMode, setThinkingMode, streamingMode, setStreamingMode, systemPrompt, setSystemPrompt } =
    useSettings();

  // Load sessions on mount
  useEffect(() => {
    const loadedSessions = getAllSessions();
    setSessions(loadedSessions);

    // Create or select a session
    if (loadedSessions.length > 0) {
      setCurrentSession(loadedSessions[0]);
    } else {
      const newSession = createNewSession(selectedModel);
      setCurrentSession(newSession);
      setSessions([newSession]);
    }
  }, []);

  const handleSessionUpdate = (updatedSession: ChatSession) => {
    setSessions((prev) =>
      prev.map((s) => (s.id === updatedSession.id ? updatedSession : s))
    );
    setCurrentSession(updatedSession);
  };

  const {
    messages,
    isLoading,
    messagesEndRef,
    clearChat,
    stopGeneration,
    sendMessage,
  } = useChatState({
    ollamaUrl,
    selectedModel,
    thinkingMode,
    streamingMode,
    systemPrompt,
    currentSession,
    onSessionUpdate: handleSessionUpdate,
  });

  const fetchModels = async () => {
    setIsLoadingModels(true);
    try {
      const response = await fetch(`${ollamaUrl}/api/tags`);
      if (!response.ok) {
        throw new Error(`Failed to fetch models: ${response.statusText}`);
      }
      const data = await response.json();
      const fetchedModels = data.models || [];
      setModels(fetchedModels);

      // Save successful URL to localStorage
      localStorage.setItem('ollamaUrl', ollamaUrl);
    } catch (error) {
      console.error("Error fetching models:", error);
      toast({
        title: "Connection Error",
        description:
          "Failed to connect to Ollama. Make sure Ollama is running on the specified URL.",
        variant: "destructive",
      });
    } finally {
      setIsLoadingModels(false);
    }
  };

  useEffect(() => {
    fetchModels();
  }, [ollamaUrl]);

  // Validate and set the selected model when models list changes
  useEffect(() => {
    if (models.length === 0) return;

    const savedModel = localStorage.getItem('selectedModel');

    // Check if we have a saved model that exists in the current models list
    if (savedModel && models.some((m) => m.name === savedModel)) {
      // Saved model is valid, use it (only set if not already set to avoid unnecessary re-renders)
      if (selectedModel !== savedModel) {
        setSelectedModel(savedModel);
      }
    } else {
      // Saved model doesn't exist or current selection is invalid
      // Use first available model
      const firstModel = models[0].name;
      setSelectedModel(firstModel);
      localStorage.setItem('selectedModel', firstModel);
    }
  }, [models]);

  const handleNewChat = () => {
    const newSession = createNewSession(selectedModel);
    setSessions((prev) => [newSession, ...prev]);
    setCurrentSession(newSession);
  };

  const handleSelectSession = (sessionId: string) => {
    // Reload from storage to get the most up-to-date version
    const allSessions = getAllSessions();
    const session = allSessions.find((s) => s.id === sessionId);
    if (session) {
      setCurrentSession(session);
      setSessions(allSessions); // Update local state
    }
  };

  const handleRenameSession = (sessionId: string, newTitle: string) => {
    updateSessionTitle(sessionId, newTitle);
    const updatedSessions = getAllSessions();
    setSessions(updatedSessions);
    if (currentSession?.id === sessionId) {
      const updated = updatedSessions.find((s) => s.id === sessionId);
      if (updated) setCurrentSession(updated);
    }
  };

  const handleDeleteSession = (sessionId: string) => {
    deleteSession(sessionId);
    const updatedSessions = getAllSessions();
    setSessions(updatedSessions);

    if (currentSession?.id === sessionId) {
      if (updatedSessions.length > 0) {
        setCurrentSession(updatedSessions[0]);
      } else {
        const newSession = createNewSession(selectedModel);
        setSessions([newSession]);
        setCurrentSession(newSession);
      }
    }
  };

  const handleTogglePin = (sessionId: string) => {
    togglePinSession(sessionId);
    const updatedSessions = getAllSessions();
    setSessions(updatedSessions);
    if (currentSession?.id === sessionId) {
      const updated = updatedSessions.find((s) => s.id === sessionId);
      if (updated) setCurrentSession(updated);
    }
  };

  const handleModelChange = (model: string) => {
    // Don't save empty model selections
    if (!model || model.trim() === '') {
      return;
    }

    setSelectedModel(model);
    localStorage.setItem('selectedModel', model);
  };

  const handleResetOllamaUrl = () => {
    setOllamaUrl(DEFAULT_OLLAMA_URL);
    localStorage.setItem('ollamaUrl', DEFAULT_OLLAMA_URL);
    toast({
      title: "Server URL Reset",
      description: "Ollama server URL has been reset to default.",
    });
  };

  return (
    <div className="flex h-screen bg-gradient-bg">
      <ChatHistoryNav
        sessions={sessions}
        currentSessionId={currentSession?.id || null}
        onSelectSession={handleSelectSession}
        onNewChat={handleNewChat}
        onRenameSession={handleRenameSession}
        onDeleteSession={handleDeleteSession}
        onTogglePin={handleTogglePin}
      />
      <div className="flex flex-col flex-1">
        {/* Header */}
        <div className="border-b border-border/50 bg-card/30 backdrop-blur-sm">
          <div className="flex items-center justify-between pl-8 pr-4 pt-4 pb-4">
            <div className="flex items-center gap-3">

            </div>

            <div className="flex items-center gap-3">
              <div className="flex items-center gap-2">
                <Label
                  htmlFor="ollama-url"
                  className="text-sm text-muted-foreground"
                >
                  Ollama Server URL:
                </Label>
                <Input
                  id="ollama-url"
                  value={ollamaUrl}
                  onChange={(e) => setOllamaUrl(e.target.value)}
                  className={cn(
                    "w-48 bg-input/50 border-border/50",
                    "focus:border-primary/50 focus:ring-1 focus:ring-primary/20"
                  )}
                  placeholder="http://localhost:11434"
                />
              </div>

              <Button
                variant="outline"
                size="icon"
                onClick={fetchModels}
                disabled={isLoadingModels}
                className={cn(
                  "border-border/50 hover:bg-transparent hover:border-primary hover:text-primary transition-colors",
                  isLoadingModels && "animate-spin"
                )}
              >
                <RefreshCw className="w-4 h-4" />
              </Button>

              <SettingsPanel
                streamingMode={streamingMode}
                onStreamingModeChange={setStreamingMode}
                systemPrompt={systemPrompt}
                onSystemPromptChange={setSystemPrompt}
                onResetOllamaUrl={handleResetOllamaUrl}
                onClearHistory={() => {
                  clearAllSessions();
                  const newSession = createNewSession(selectedModel);
                  setSessions([newSession]);
                  setCurrentSession(newSession);
                  toast({
                    title: "History Cleared",
                    description: "All chat history has been removed.",
                  });
                }}
              />
            </div>
          </div>
        </div>

        {/* Messages */}
        <div className="flex-1 overflow-y-auto">
          {messages.length === 0 ? (
            <div className="flex items-center justify-center h-full">
              <div className="text-center max-w-md mx-auto p-8">
                <h2 className="text-2xl font-semibold text-foreground mb-2">
                  Welcome to Simple Ollama Chat
                </h2>
                <p className="text-muted-foreground">
                  Start a conversation with your AI assistant. Select a model
                  and type your message below.
                </p>
              </div>
            </div>
          ) : (
            <div className="max-w-4xl mx-auto">
              {messages.map((message, index) => {
                // Check if this is the last message and thinking is currently active
                const isLastMessage = index === messages.length - 1;
                const isThinkingActive =
                  isLastMessage &&
                  message.role === "assistant" &&
                  thinkingMode &&
                  isLoading;

                return (
                  <ChatMessage
                    key={message.id}
                    message={message}
                    isThinkingActive={isThinkingActive}
                  />
                );
              })}
              {isLoading && (
                <div className="flex justify-start p-4">
                  <div className="flex items-center gap-3">
                    <div className="w-8 h-8 rounded-full bg-gradient-ai flex items-center justify-center shadow-card">
                      <div className="w-4 h-4 rounded-full bg-accent animate-pulse" />
                    </div>
                    <div className="bg-gradient-ai text-ai-message-foreground rounded-lg px-4 py-3 shadow-card">
                      <div className="flex space-x-1">
                        <div className="w-2 h-2 bg-accent rounded-full animate-bounce" />
                        <div
                          className="w-2 h-2 bg-accent rounded-full animate-bounce"
                          style={{ animationDelay: "0.1s" }}
                        />
                        <div
                          className="w-2 h-2 bg-accent rounded-full animate-bounce"
                          style={{ animationDelay: "0.2s" }}
                        />
                      </div>
                    </div>
                  </div>
                </div>
              )}
              <div ref={messagesEndRef} />
            </div>
          )}
        </div>

        {/* Input */}
        <ChatInput
          onSendMessage={sendMessage}
          isLoading={isLoading}
          onStop={stopGeneration}
          disabled={!selectedModel}
          thinkingMode={thinkingMode}
          onThinkingModeChange={setThinkingMode}
          selectedModel={selectedModel}
          onModelChange={handleModelChange}
          models={models}
          isLoadingModels={isLoadingModels}
        />
      </div>
    </div>
  );
}
