import { useState } from "react";
import { Switch } from "@/components/ui/switch";
import { Label } from "@/components/ui/label";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Zap, Sun, Moon, Settings, Trash2, Globe, Brain } from "lucide-react";
import { useTheme } from "next-themes";
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from "@/components/ui/popover";
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

interface SettingsPanelProps {
  streamingMode: boolean;
  onStreamingModeChange: (enabled: boolean) => void;
  systemPrompt: string;
  onSystemPromptChange: (prompt: string) => void;
  onClearHistory?: () => void;
  onResetOllamaUrl?: () => void;
}

export function SettingsPanel({
  streamingMode,
  onStreamingModeChange,
  systemPrompt,
  onSystemPromptChange,
  onClearHistory,
  onResetOllamaUrl,
}: SettingsPanelProps) {
  const { theme, setTheme } = useTheme();
  const [showClearDialog, setShowClearDialog] = useState(false);

  const handleClearHistory = () => {
    onClearHistory?.();
    setShowClearDialog(false);
  };

  return (
    <>
      <Popover>
      <PopoverTrigger asChild>
        <Button
          variant="outline"
          size="icon"
          className="border-border/50 hover:bg-transparent hover:border-primary hover:text-primary transition-colors"
        >
          <Settings className="w-4 h-4" />
        </Button>
      </PopoverTrigger>
      <PopoverContent className="w-80 bg-card/95 backdrop-blur-sm border-border/50" align="end">
        <div className="space-y-6">
          <div className="space-y-2">
            <h4 className="font-medium text-foreground">Settings</h4>
            <p className="text-sm text-muted-foreground">
              Configure your chat experience
            </p>
          </div>

          <div className="space-y-4">
            {/* System Prompt */}
            <div className="space-y-2">
              <div className="flex items-center space-x-2">
                <Brain className="w-4 h-4 text-muted-foreground" />
                <Label htmlFor="system-prompt" className="text-sm">
                  System Prompt
                </Label>
              </div>
              <Textarea
                id="system-prompt"
                value={systemPrompt}
                onChange={(e) => onSystemPromptChange(e.target.value)}
                placeholder="Enter a system prompt that will be sent with every message..."
                className="min-h-[80px] resize-none"
                rows={3}
              />
              <p className="text-xs text-muted-foreground">
                This prompt will be included with every chat request to guide the AI's behavior.
              </p>
            </div>

            {/* Theme Toggle */}
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-2">
                {theme === "dark" ? (
                  <Moon className="w-4 h-4 text-muted-foreground" />
                ) : (
                  <Sun className="w-4 h-4 text-muted-foreground" />
                )}
                <Label htmlFor="theme-toggle" className="text-sm">
                  Dark Mode
                </Label>
              </div>
              <Switch
                id="theme-toggle"
                checked={theme === "dark"}
                onCheckedChange={(checked) => setTheme(checked ? "dark" : "light")}
              />
            </div>



            {/* Streaming Mode Toggle */}
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-2">
                <Zap className="w-4 h-4 text-muted-foreground" />
                <div className="space-y-0.5">
                  <Label htmlFor="streaming-toggle" className="text-sm">
                    Streaming Mode
                  </Label>
                  <p className="text-xs text-muted-foreground">
                    Real-time response streaming
                  </p>
                </div>
              </div>
              <Switch
                id="streaming-toggle"
                checked={streamingMode}
                onCheckedChange={onStreamingModeChange}
              />
            </div>

            {/* Action Buttons */}
            {(onResetOllamaUrl || onClearHistory) && (
              <div className="pt-4 border-t border-border/50 space-y-2">
                {onResetOllamaUrl && (
                    <Button
                    variant="outline"
                    className="w-full"
                    onClick={onResetOllamaUrl}
                    >
                    <Globe className="w-4 h-4 mr-2" />
                    Use Default Server URL
                    </Button>
                )}

                {onClearHistory && (
                  <Button
                    variant="destructive"
                    className="w-full"
                    onClick={() => setShowClearDialog(true)}
                  >
                    <Trash2 className="w-4 h-4 mr-2" />
                    Clear All Chat History
                  </Button>
                )}
              </div>
            )}
          </div>
        </div>
      </PopoverContent>
    </Popover>

    {/* Clear History Confirmation Dialog */}
    <AlertDialog open={showClearDialog} onOpenChange={setShowClearDialog}>
      <AlertDialogContent>
        <AlertDialogHeader>
          <AlertDialogTitle>Clear All Chat History</AlertDialogTitle>
          <AlertDialogDescription>
            Are you sure you want to delete all chat sessions? This action
            cannot be undone and all your chat history will be permanently
            removed from local storage.
          </AlertDialogDescription>
        </AlertDialogHeader>
        <AlertDialogFooter>
          <AlertDialogCancel>Cancel</AlertDialogCancel>
          <AlertDialogAction
            onClick={handleClearHistory}
            className="bg-destructive hover:bg-destructive/90"
          >
            Clear All
          </AlertDialogAction>
        </AlertDialogFooter>
      </AlertDialogContent>
    </AlertDialog>
    </>
  );
}
