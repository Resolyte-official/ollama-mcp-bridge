import { cn } from "@/lib/utils";
import { Bot, User, Brain } from "lucide-react";
import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from "@/components/ui/collapsible";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

interface ChatMessageProps {
  message: {
    id: string;
    content: string;
    role: 'user' | 'assistant';
    timestamp: Date;
    thinking?: string;
  };
  isThinkingActive?: boolean;
}

export function ChatMessage({ message, isThinkingActive = false }: ChatMessageProps) {
  const isUser = message.role === 'user';
  const [showThinking, setShowThinking] = useState(false);
  const hasThinking = message.thinking && message.thinking.length > 0;

  // Auto-open when thinking is active, auto-collapse when done
  useEffect(() => {
    if (isThinkingActive && hasThinking) {
      setShowThinking(true);
    }
  }, [isThinkingActive, hasThinking]);

  // Separate effect to handle auto-collapse when thinking is complete
  useEffect(() => {
    if (!isThinkingActive && hasThinking && showThinking) {
      // Add a small delay before collapsing to let user see the final thinking
      const timer = setTimeout(() => setShowThinking(false), 1000);
      return () => clearTimeout(timer);
    }
  }, [isThinkingActive]);

  return (
    <div
      className={cn(
        "flex gap-3 p-4 animate-slide-up",
        isUser ? "justify-end" : "justify-start"
      )}
    >
      {!isUser && (
        <div className="flex-shrink-0 w-9 h-9 rounded-full bg-gradient-ai flex items-center justify-center shadow-card">
          <Bot className="w-6 h-6 text-accent" />
        </div>
      )}

      <div
        className={cn(
          "max-w-[80%] space-y-2",
          isUser ? "ml-12" : "mr-12"
        )}
      >
        {/* Thinking Process */}
        {hasThinking && (
          <Collapsible open={showThinking} onOpenChange={setShowThinking}>
            <CollapsibleTrigger asChild>
              <Button
                variant="ghost"
                size="sm"
                className="h-6 px-2 text-xs text-muted-foreground transition-colors"
              >
                <Brain className="w-4 h-4" />
                {showThinking ? 'Hide' : 'Show'} thinking process
              </Button>
            </CollapsibleTrigger>

            <CollapsibleContent className="space-y-2">
              <div className={cn(
                "bg-muted/30 border border-border/30 rounded-lg px-3 py-2",
                isThinkingActive ? "thinking-shimmer" : ""
              )}>
                <div className="flex items-center gap-2 mb-2">
                  <Brain className={cn(
                    "w-3 h-3 text-muted-foreground",
                    isThinkingActive ? "animate-pulse" : ""
                  )} />
                  <span className="text-xs text-muted-foreground font-medium">
                    {isThinkingActive ? "Thinking..." : "Thought process"}
                  </span>
                </div>
                <p className="text-xs leading-relaxed text-muted-foreground whitespace-pre-wrap">
                  {message.thinking}
                </p>
              </div>
            </CollapsibleContent>
          </Collapsible>
        )}

        {/* Main Message */}
        <div
          className={cn(
            "rounded-lg px-4 py-3 shadow-card",
            isUser
              ? "bg-gradient-user text-user-message-foreground"
              : "bg-gradient-ai text-ai-message-foreground"
          )}
        >
          {isUser ? (
            <p className="text-sm leading-relaxed whitespace-pre-wrap">{message.content}</p>
          ) : (
            <div className="prose prose-sm dark:prose-invert max-w-none prose-pre:bg-muted/50 prose-pre:text-foreground">
              <ReactMarkdown remarkPlugins={[remarkGfm]}>
                {message.content}
              </ReactMarkdown>
            </div>
          )}
          <span className="text-xs opacity-70 mt-2 block">
            {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
          </span>
        </div>
      </div>

      {isUser && (
        <div className="flex-shrink-0 w-9 h-9 rounded-full bg-gradient-user flex items-center justify-center shadow-glow">
          <User className="w-5 h-5 text-user-message-foreground" />
        </div>
      )}
    </div>
  );
}
