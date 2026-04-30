import { useState, useEffect } from "react";

export function useSettings() {
  const [thinkingMode, setThinkingMode] = useState(false);
  const [streamingMode, setStreamingMode] = useState(true);
  const [systemPrompt, setSystemPrompt] = useState("");

  // Load settings from localStorage
  useEffect(() => {
    const savedThinkingMode = localStorage.getItem('thinkingMode');
    const savedStreamingMode = localStorage.getItem('streamingMode');
    const savedSystemPrompt = localStorage.getItem('systemPrompt');
    
    if (savedThinkingMode !== null) {
      setThinkingMode(JSON.parse(savedThinkingMode));
    }
    if (savedStreamingMode !== null) {
      setStreamingMode(JSON.parse(savedStreamingMode));
    }
    if (savedSystemPrompt !== null) {
      setSystemPrompt(savedSystemPrompt);
    }
  }, []);

  // Save settings to localStorage
  useEffect(() => {
    localStorage.setItem('thinkingMode', JSON.stringify(thinkingMode));
  }, [thinkingMode]);

  useEffect(() => {
    localStorage.setItem('streamingMode', JSON.stringify(streamingMode));
  }, [streamingMode]);

  useEffect(() => {
    localStorage.setItem('systemPrompt', systemPrompt);
  }, [systemPrompt]);

  return {
    thinkingMode,
    setThinkingMode,
    streamingMode,
    setStreamingMode,
    systemPrompt,
    setSystemPrompt,
  };
}