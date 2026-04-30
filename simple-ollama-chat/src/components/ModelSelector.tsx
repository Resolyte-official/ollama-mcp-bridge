import { useState, useEffect } from "react";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Button } from "@/components/ui/button";
import { RefreshCw, Settings } from "lucide-react";
import { cn } from "@/lib/utils";
import { useToast } from "@/hooks/use-toast";

interface ModelSelectorProps {
  selectedModel: string;
  onModelChange: (model: string) => void;
  ollamaUrl: string;
}

interface OllamaModel {
  name: string;
  model: string;
  size: number;
  digest: string;
  details: {
    format: string;
    family: string;
    families: string[];
    parameter_size: string;
    quantization_level: string;
  };
}

export function ModelSelector({ selectedModel, onModelChange, ollamaUrl }: ModelSelectorProps) {
  const [models, setModels] = useState<OllamaModel[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const { toast } = useToast();

  const fetchModels = async () => {
    setIsLoading(true);
    try {
      const response = await fetch(`${ollamaUrl}/api/tags`);
      if (!response.ok) {
        throw new Error(`Failed to fetch models: ${response.statusText}`);
      }
      const data = await response.json();
      setModels(data.models || []);
    } catch (error) {
      console.error('Error fetching models:', error);
      toast({
        title: "Connection Error",
        description: "Failed to connect to Ollama. Make sure Ollama is running on the specified URL.",
        variant: "destructive",
      });
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchModels();
  }, [ollamaUrl]);

  const formatModelSize = (bytes: number) => {
    const gb = bytes / (1024 * 1024 * 1024);
    return `${gb.toFixed(1)}GB`;
  };

  return (
    <div className="flex items-center gap-3 p-4 border-b border-border/50 bg-card/30 backdrop-blur-sm">
      {/* <Settings className="w-5 h-5 text-muted-foreground" />Model Selection */}

      <div className="flex-1">
        <Select value={selectedModel} onValueChange={onModelChange} disabled={isLoading}>
          <SelectTrigger className={cn(
            "border-border/50",
            "hover:bg-transparent hover:border-foreground hover:text-foreground",
            "focus:border-foreground focus:ring-1 focus:ring-foreground/20",
            "transition-all duration-200"
          )}>
            <SelectValue placeholder="Select a model..." />
          </SelectTrigger>
          <SelectContent className="border-border/50">
            {models.map((model) => (
              <SelectItem
                key={model.name}
                value={model.name}
              >
                <div className="flex items-center justify-between w-full">
                  <span className="font-medium">{model.name}</span>
                  <span className="text-xs ml-4">
                    {formatModelSize(model.size)}
                  </span>
                </div>
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>

      <Button
        variant="outline"
        size="icon"
        onClick={fetchModels}
        disabled={isLoading}
        className={cn(
          "border-border/50 hover:bg-transparent hover:border-primary hover:text-primary transition-colors",
          isLoading && "animate-spin"
        )}
      >
        <RefreshCw className="w-4 h-4" />
      </Button>
    </div>
  );
}
