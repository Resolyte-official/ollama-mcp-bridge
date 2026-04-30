import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  Menu,
  MoreVertical,
  Pencil,
  Trash2,
  Pin,
  PinOff,
  MessageSquare,
  SquarePen,
} from "lucide-react";
import { cn } from "@/lib/utils";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from "@/components/ui/alert-dialog";
import {
  Tooltip,
  TooltipContent,
  TooltipTrigger,
} from "@/components/ui/tooltip";
import type { ChatSession } from "@/lib/chatHistory";

interface ChatHistoryNavProps {
  sessions: ChatSession[];
  currentSessionId: string | null;
  onSelectSession: (sessionId: string) => void;
  onNewChat: () => void;
  onRenameSession: (sessionId: string, newTitle: string) => void;
  onDeleteSession: (sessionId: string) => void;
  onTogglePin: (sessionId: string) => void;
}

export function ChatHistoryNav({
  sessions,
  currentSessionId,
  onSelectSession,
  onNewChat,
  onRenameSession,
  onDeleteSession,
  onTogglePin,
}: ChatHistoryNavProps) {
  const [isCollapsed, setIsCollapsed] = useState(false);
  const [editingId, setEditingId] = useState<string | null>(null);
  const [editTitle, setEditTitle] = useState("");
  const [deleteConfirmId, setDeleteConfirmId] = useState<string | null>(null);

  const sortedSessions = [...sessions].sort((a, b) => {
    if (a.isPinned && !b.isPinned) return -1;
    if (!a.isPinned && b.isPinned) return 1;
    return b.updatedAt.getTime() - a.updatedAt.getTime();
  });

  const handleStartEdit = (session: ChatSession) => {
    setEditingId(session.id);
    setEditTitle(session.title);
  };

  const handleSaveEdit = (sessionId: string) => {
    if (editTitle.trim()) {
      onRenameSession(sessionId, editTitle.trim());
    }
    setEditingId(null);
    setEditTitle("");
  };

  const handleCancelEdit = () => {
    setEditingId(null);
    setEditTitle("");
  };

  const handleDeleteClick = (sessionId: string) => {
    setDeleteConfirmId(sessionId);
  };

  const handleConfirmDelete = () => {
    if (deleteConfirmId) {
      onDeleteSession(deleteConfirmId);
      setDeleteConfirmId(null);
    }
  };

  return (
    <>
      <div
        className={cn(
          "h-screen bg-card/30 backdrop-blur-sm border-r border-border/50 transition-all duration-300 flex flex-col",
          isCollapsed ? "w-16" : "w-80"
        )}
      >
        {/* Header */}
        <div className="p-4 border-b border-border/50 flex items-center justify-between gap-2">
          {!isCollapsed ? (
            <div className="flex items-center gap-3">
              <div className="relative inline-flex items-center justify-center flex-shrink-0">
                {/* Ollama icon */}
                <div className="w-10 h-10 rounded-full bg-white flex items-center justify-center border border-border/20">
                  <img
                    src="/ollama-icon.png"
                    alt="Ollama"
                    className="h-7 w-auto filter brightness-0"
                  />
                </div>
                {/* Message square positioned to look like it's coming from the icon */}
                <div className="absolute -right-2 -top-2 w-5 h-5 bg-white rounded-full flex items-center justify-center">
                  <MessageSquare className="w-3 h-3 text-primary" />
                </div>
              </div>
              <div className="flex flex-col min-w-0">
                <h2 className="text-sm font-semibold text-foreground truncate">
                  Simple Ollama Chat
                </h2>
              </div>
            </div>
          ) : (
            <Tooltip>
              <TooltipTrigger asChild>
                <button
                  onClick={() => setIsCollapsed(false)}
                  className="group relative inline-flex items-center justify-center mx-auto cursor-e-resize z-50"
                >
                  {/* Logo - visible by default, hidden on hover */}
                  <div className="relative inline-flex items-center justify-center group-hover:opacity-0 transition-opacity">
                    {/* Ollama icon */}
                    <div className="w-10 h-10 rounded-full bg-white flex items-center justify-center border border-border/20">
                      <img
                        src="/ollama-icon.png"
                        alt="Ollama"
                        className="h-7 w-auto filter brightness-0"
                      />
                    </div>
                    {/* Message square positioned to look like it's coming from the icon */}
                    <div className="absolute -right-1 -top-1 w-4 h-4 bg-white rounded-full flex items-center justify-center">
                      <MessageSquare className="w-2.5 h-2.5 text-primary" />
                    </div>
                  </div>
                  {/* Menu icon - hidden by default, visible on hover */}
                  <div className="absolute inset-0 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity">
                    <Menu className="w-5 h-5 text-primary" />
                  </div>
                </button>
              </TooltipTrigger>
              <TooltipContent side="right" className="z-[100]">
                <p>Open navbar</p>
              </TooltipContent>
            </Tooltip>
          )}
          {!isCollapsed && (
            <Tooltip>
              <TooltipTrigger asChild>
                <Button
                  variant="ghost"
                  size="icon"
                  onClick={() => setIsCollapsed(!isCollapsed)}
                  className="hover:bg-transparent hover:text-primary flex-shrink-0"
                >
                  <Menu className="w-4 h-4" />
                </Button>
              </TooltipTrigger>
              <TooltipContent side="right" className="z-[100]">
                <p>Collapse sidebar</p>
              </TooltipContent>
            </Tooltip>
          )}
        </div>

        {/* New Chat Button */}
        <div className="p-3">
          <Tooltip>
            <TooltipTrigger asChild>
              <Button
                onClick={onNewChat}
                variant="outline"
                className={cn(
                  "w-full h-9 border-border/50 hover:bg-transparent hover:border-primary hover:text-primary",
                  isCollapsed && "px-0"
                )}
              >
                <SquarePen className="w-4 h-4" />
                {!isCollapsed && <span className="ml-2 text-sm">New Chat</span>}
              </Button>
            </TooltipTrigger>
            <TooltipContent side="right" className="z-[100]">
              <p>Start a new chat</p>
            </TooltipContent>
          </Tooltip>
        </div>

        {/* Chat List */}
        <div className="flex-1 overflow-y-auto px-2">
          {sortedSessions.map((session) => (
            <div
              key={session.id}
              className={cn(
                "group relative mb-1 rounded-md transition-colors border border-transparent",
                currentSessionId === session.id
                  ? "bg-primary/10 border-primary/50"
                  : "hover:border-primary/50"
              )}
            >
              {editingId === session.id ? (
                <div className="p-2">
                  <Input
                    value={editTitle}
                    onChange={(e) => setEditTitle(e.target.value)}
                    onKeyDown={(e) => {
                      if (e.key === "Enter") {
                        handleSaveEdit(session.id);
                      } else if (e.key === "Escape") {
                        handleCancelEdit();
                      }
                    }}
                    onBlur={() => handleSaveEdit(session.id)}
                    autoFocus
                    className="h-8 text-sm"
                  />
                </div>
              ) : (
                <div className="flex items-center">
                  <Tooltip>
                    <TooltipTrigger asChild>
                      <button
                        onClick={() => onSelectSession(session.id)}
                        className={cn(
                          "flex-1 text-left px-3 py-2 rounded-md transition-colors min-w-0",
                          isCollapsed ? "justify-center" : ""
                        )}
                      >
                        <div className="flex items-center gap-2 min-w-0">
                          {session.isPinned && !isCollapsed && (
                            <Pin className="w-3 h-3 text-primary flex-shrink-0" />
                          )}
                          <MessageSquare className="w-4 h-4 text-muted-foreground flex-shrink-0" />
                          {!isCollapsed && (
                            <span className="text-sm truncate flex-1 block overflow-hidden text-ellipsis whitespace-nowrap">
                              {session.title}
                            </span>
                          )}
                        </div>
                      </button>
                    </TooltipTrigger>
                    {isCollapsed && (
                      <TooltipContent side="right">
                        <div className="flex items-center gap-2">
                          {session.isPinned && (
                            <Pin className="w-3 h-3 text-primary" />
                          )}
                          <p className="max-w-xs truncate">{session.title}</p>
                        </div>
                      </TooltipContent>
                    )}
                  </Tooltip>

                  {!isCollapsed && (
                    <DropdownMenu>
                      <DropdownMenuTrigger asChild>
                        <Button
                          variant="ghost"
                          size="icon"
                          className="opacity-0 group-hover:opacity-100 h-8 w-8 mr-1 hover:bg-transparent hover:text-foreground transition-colors"
                        >
                          <MoreVertical className="w-4 h-4" />
                        </Button>
                      </DropdownMenuTrigger>
                      <DropdownMenuContent align="end" className="border-border/50">
                        <DropdownMenuItem
                          onClick={() => handleStartEdit(session)}
                        >
                          <Pencil className="w-4 h-4 mr-2" />
                          Rename
                        </DropdownMenuItem>
                        <DropdownMenuItem
                          onClick={() => onTogglePin(session.id)}
                        >
                          {session.isPinned ? (
                            <>
                              <PinOff className="w-4 h-4 mr-2" />
                              Unpin
                            </>
                          ) : (
                            <>
                              <Pin className="w-4 h-4 mr-2" />
                              Pin
                            </>
                          )}
                        </DropdownMenuItem>
                        <DropdownMenuItem
                          onClick={() => handleDeleteClick(session.id)}
                          className="text-destructive hover:bg-destructive/10 hover:text-destructive focus:text-destructive"
                        >
                          <Trash2 className="w-4 h-4 mr-2" />
                          Delete
                        </DropdownMenuItem>
                      </DropdownMenuContent>
                    </DropdownMenu>
                  )}
                </div>
              )}
            </div>
          ))}
        </div>
      </div>

      {/* Delete Confirmation Dialog */}
      <AlertDialog
        open={deleteConfirmId !== null}
        onOpenChange={(open) => !open && setDeleteConfirmId(null)}
      >
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Delete Chat</AlertDialogTitle>
            <AlertDialogDescription>
              Are you sure you want to delete this chat? This action cannot be
              undone.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>Cancel</AlertDialogCancel>
            <AlertDialogAction
              onClick={handleConfirmDelete}
              className="bg-destructive hover:bg-destructive/90"
            >
              Delete
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </>
  );
}
